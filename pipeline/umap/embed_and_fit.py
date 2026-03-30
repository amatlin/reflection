"""Embed responses and fit UMAP to produce 2D coordinates.

Reads seed_data.json (and optionally real responses from BigQuery),
embeds all texts with OpenAI text-embedding-3-small, fits UMAP,
and outputs coordinates.json + umap_model.pkl.

Usage:
    conda activate reflection
    python pipeline/umap/embed_and_fit.py

Requires OPENAI_API_KEY in environment or .env file.
"""

import json
import pickle
from pathlib import Path

import numpy as np
import umap
from openai import OpenAI

SEED_PATH = Path(__file__).parent / "seed_data.json"
COORDS_PATH = Path(__file__).parent / "coordinates.json"
MODEL_PATH = Path(__file__).parent / "umap_model.pkl"

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI embeddings batch size


def load_responses() -> list[dict]:
    """Load seed data and return list of {text, is_synthetic} dicts."""
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"Run seed_responses.py first: {SEED_PATH}")

    with open(SEED_PATH) as f:
        responses = json.load(f)

    # TODO: also fetch real responses from BigQuery and merge them in
    # with is_synthetic=False

    print(f"Loaded {len(responses)} responses ({sum(1 for r in responses if r['is_synthetic'])} synthetic)")
    return responses


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
    responses = load_responses()
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
                "is_synthetic": r["is_synthetic"],
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
