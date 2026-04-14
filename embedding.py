from pathlib import Path
from loguru import logger
import pandas as pd
from sentence_transformers import SentenceTransformer

from logging_utils import setup_logger


INPUT_FILE = "social_data.xlsx"
OUTPUT_FILE = "file_with_embeddings.xlsx"
TEXT_COLUMN = "text"
EMBEDDING_COLUMN = "embedding"
MODEL_NAME = "all-MiniLM-L6-v2"


def main() -> None:
    setup_logger()
    logger.info("Starting embedding pipeline. input={}, output={}", INPUT_FILE, OUTPUT_FILE)
    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    logger.info("Loaded {} rows from {}", len(df), INPUT_FILE)
    if TEXT_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {TEXT_COLUMN}")

    texts = df[TEXT_COLUMN].fillna("").tolist()

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts)
    logger.info("Generated embeddings using model={}", MODEL_NAME)

    df[EMBEDDING_COLUMN] = embeddings.tolist()
    df.to_excel(OUTPUT_FILE, index=False)
    logger.info("Saved embeddings to {}", OUTPUT_FILE)


if __name__ == "__main__":
    try:
        main()
        logger.info("Embedding pipeline completed successfully.")
    except Exception as exc:
        logger.exception("Embedding pipeline failed: {}", exc)
