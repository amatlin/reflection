"""Generate synthetic seed responses for the UMAP visualization.

Produces ~200 varied responses that simulate what visitors might type
when prompted with "what do you make of it?" on a self-referential website.

Usage:
    conda activate reflection
    python pipeline/umap/seed_responses.py

Requires ANTHROPIC_API_KEY in environment or .env file.
Outputs pipeline/umap/seed_data.json.
"""

import json
import os
from pathlib import Path

import anthropic

OUTPUT_PATH = Path(__file__).parent / "seed_data.json"
BATCH_SIZE = 50  # responses per API call
NUM_BATCHES = 4  # 4 × 50 = 200 responses

PROMPT = """You are generating synthetic visitor responses for a self-referential art website called Reflection. The site tracks its own analytics and shows them to visitors. At the end of the exhibit, visitors are asked: "what do you make of it?"

Generate {batch_size} unique responses. They should feel like real people typed them — varied in length (3 words to 2 sentences), tone (amused, confused, philosophical, bored, delighted, cynical, earnest), and perspective. Some people get it, some don't, some overthink it, some barely engage.

Examples of the range:
- "lol what"
- "This is genuinely unsettling in a way I can't articulate"
- "so it's just... watching me watch it?"
- "I work in data engineering and this is painfully accurate"
- "art"
- "feels like being in a panopticon but the guards are also prisoners"
- "neat"
- "I don't get it but I like it"

Return ONLY a JSON array of strings, no other text. Each response should be unique and between 2-150 characters."""


def generate_batch(client: anthropic.Anthropic, batch_num: int) -> list[str]:
    """Generate one batch of synthetic responses."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(batch_size=BATCH_SIZE),
            }
        ],
    )
    text = message.content[0].text.strip()
    # Parse JSON array from response
    responses = json.loads(text)
    print(f"  Batch {batch_num + 1}/{NUM_BATCHES}: got {len(responses)} responses")
    return responses


def main():
    client = anthropic.Anthropic()
    all_responses = []

    print(f"Generating {NUM_BATCHES * BATCH_SIZE} synthetic responses...")
    for i in range(NUM_BATCHES):
        batch = generate_batch(client, i)
        all_responses.extend(batch)

    # Deduplicate
    unique = list(dict.fromkeys(all_responses))
    print(f"Total unique responses: {len(unique)}")

    # Save with is_synthetic flag
    seed_data = [
        {"text": r, "is_synthetic": True}
        for r in unique
    ]

    OUTPUT_PATH.write_text(json.dumps(seed_data, indent=2))
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
