from pathlib import Path
from sentence_transformers import SentenceTransformer

import pandas as pd


INPUT_FILE = "social_data.xlsx"
OUTPUT_FILE = "file_with_embeddings.xlsx"
TEXT_COLUMN = "text"
EMBEDDING_COLUMN = "embedding"
MODEL_NAME = "all-MiniLM-L6-v2"


def main() -> None:
    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    if TEXT_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {TEXT_COLUMN}")

    texts = df[TEXT_COLUMN].fillna("").tolist()

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts)

    df[EMBEDDING_COLUMN] = embeddings.tolist()
    df.to_excel(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    try:
        main()
        print(f"Done. Output saved to: {OUTPUT_FILE}")
    except Exception as exc:
        print(f"Error: {exc}")
