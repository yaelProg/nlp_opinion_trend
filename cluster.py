from __future__ import annotations
from pathlib import Path
from sklearn.cluster import KMeans
from pathlib import Path
from sklearn.cluster import KMeans

import ast
import numpy as np
import pandas as pd


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
    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    if EMBEDDING_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {EMBEDDING_COLUMN}")

    embedding_list = df[EMBEDDING_COLUMN].apply(_parse_embedding).tolist()
    if not embedding_list:
        raise ValueError("No embeddings found to cluster.")

    embedding_matrix = np.array(embedding_list, dtype=float)
    if len(embedding_matrix) < N_CLUSTERS:
        raise ValueError(
            f"Not enough rows ({len(embedding_matrix)}) for N_CLUSTERS={N_CLUSTERS}."
        )

    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    labels = model.fit_predict(embedding_matrix)

    df[CLUSTER_COLUMN] = labels
    df.to_excel(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    try:
        main()
        print(f"Done. Output saved to: {OUTPUT_FILE}")
    except Exception as exc:
        print(f"Error: {exc}")