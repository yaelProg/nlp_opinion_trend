from __future__ import annotations
from pathlib import Path
from sklearn.cluster import KMeans

import ast
import numpy as np
import pandas as pd

from loguru import logger
from logging_utils import setup_logger


INPUT_FILE = "file_with_embeddings.xlsx"
OUTPUT_FILE = "file_with_clusters.xlsx"
EMBEDDING_COLUMN = "embedding"
CLUSTER_COLUMN = "cluster"
N_CLUSTERS = 5
RANDOM_STATE = 42


def _parse_embedding(value: object) -> list[float]:
    if isinstance(value, list):
        return [float(x) for x in value]
    if isinstance(value, np.ndarray):
        return value.astype(float).tolist()
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [float(x) for x in parsed]
    raise ValueError("Embedding value is not a valid vector.")


def main() -> None:
    setup_logger()
    logger.info("Starting clustering flow. input={}, output={}", INPUT_FILE, OUTPUT_FILE)
    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    logger.info("Loaded {} rows from Excel", len(df))
    if EMBEDDING_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {EMBEDDING_COLUMN}")

    logger.info("Parsing embeddings from column: {}", EMBEDDING_COLUMN)
    embedding_list = df[EMBEDDING_COLUMN].apply(_parse_embedding).tolist()
    if not embedding_list:
        raise ValueError("No embeddings found to cluster.")

    embedding_matrix = np.array(embedding_list, dtype=float)
    logger.info("Parsed embedding matrix with shape: {}", embedding_matrix.shape)
    if len(embedding_matrix) < N_CLUSTERS:
        raise ValueError(
            f"Not enough rows ({len(embedding_matrix)}) for N_CLUSTERS={N_CLUSTERS}."
        )

    logger.info("Running KMeans with n_clusters={}, random_state={}", N_CLUSTERS, RANDOM_STATE)
    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    labels = model.fit_predict(embedding_matrix)
    logger.info("Clustering complete.")

    df[CLUSTER_COLUMN] = labels
    df.to_excel(OUTPUT_FILE, index=False)
    logger.info("Saved clustered output to: {}", OUTPUT_FILE)


if __name__ == "__main__":
    try:
        main()
        logger.info("Cluster pipeline completed successfully.")
    except Exception as exc:
        logger.exception("Cluster pipeline failed: {}", exc)