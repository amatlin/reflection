"""Embed responses and fit UMAP to produce 2D coordinates.

Fetches real questionnaire responses from BigQuery, embeds them with
OpenAI text-embedding-3-small, fits UMAP, and outputs coordinates.json
+ umap_model.pkl.

Only runs if there are enough responses (MIN_RESPONSES). Below that threshold, exits early.

Usage:
    conda activate reflection
    python pipeline/umap/embed_and_fit.py

Requires OPENAI_API_KEY and BigQuery credentials in environment or .env file.
"""

import json
import os
import pickle
from pathlib import Path

import numpy as np
import umap
from google.cloud import bigquery
from google.oauth2 import service_account
from openai import OpenAI

COORDS_PATH = Path(__file__).parent / "coordinates.json"
MODEL_PATH = Path(__file__).parent / "umap_model.pkl"

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100
MIN_RESPONSES = 50

# BigQuery config — mirrors app/config.py defaults
BQ_PROJECT = os.environ.get("BIGQUERY_PROJECT", "reflection-data")
BQ_DATASET = os.environ.get("BIGQUERY_DATASET", "reflection")
BQ_KEY_JSON = os.environ.get("BIGQUERY_KEY_JSON", "")
BQ_KEY_PATH = os.environ.get("BIGQUERY_KEY_PATH", "")


def get_bq_client() -> bigquery.Client:
    """Create a BigQuery client from environment credentials."""
    if BQ_KEY_JSON:
        info = json.loads(BQ_KEY_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        return bigquery.Client(project=BQ_PROJECT, credentials=credentials)
    elif BQ_KEY_PATH:
        credentials = service_account.Credentials.from_service_account_file(
            BQ_KEY_PATH, scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        return bigquery.Client(project=BQ_PROJECT, credentials=credentials)
    else:
        return bigquery.Client(project=BQ_PROJECT)


def fetch_responses() -> list[dict]:
    """Fetch questionnaire responses from BigQuery."""
    client = get_bq_client()
    table = f"{BQ_PROJECT}.{BQ_DATASET}.questionnaire_responses"
    query = f"SELECT response_text FROM `{table}` WHERE response_text IS NOT NULL"
    rows = list(client.query(query).result())
    return [{"text": row.response_text} for row in rows]


def embed_texts(client: OpenAI, texts: list[str]) -> np.ndarray:
    """Embed texts using OpenAI API, returns (n, dim) array."""
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")

    return np.array(all_embeddings)


def fit_umap(embeddings: np.ndarray) -> tuple[np.ndarray, umap.UMAP]:
    """Fit UMAP and return 2D coordinates + fitted model."""
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.1,
        metric="cosine",
        random_state=42,
    )
    coords = reducer.fit_transform(embeddings)
    print(f"  UMAP fit complete: {coords.shape}")
    return coords, reducer


def main():
    print("Fetching responses from BigQuery...")
    responses = fetch_responses()
    print(f"Found {len(responses)} responses")

    if len(responses) < MIN_RESPONSES:
        print(f"Need {MIN_RESPONSES} responses to fit UMAP, only have {len(responses)}. Exiting.")
        return

    texts = [r["text"] for r in responses]

    print("Embedding responses...")
    client = OpenAI()
    embeddings = embed_texts(client, texts)

    print("Fitting UMAP...")
    coords, reducer = fit_umap(embeddings)

    # Build output with coordinates
    output = []
    for i, r in enumerate(responses):
        output.append(
            {
                "x": float(coords[i, 0]),
                "y": float(coords[i, 1]),
                "text": r["text"],
            }
        )

    COORDS_PATH.write_text(json.dumps(output, indent=2))
    print(f"Saved coordinates to {COORDS_PATH}")

    # Pickle is safe here — we generate and load our own model, not untrusted content.
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(reducer, f)
    print(f"Saved UMAP model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
