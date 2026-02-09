import logging
import os

import pandas as pd

from processing.application.ports.dataset_state_port import DatasetStatePort

logger = logging.getLogger(__name__)


class ParquetDatasetStateAdapter(DatasetStatePort):

    def __init__(self, ingestion_dir: str, processing_dir: str):
        self._dataset_hash_path = os.path.join(ingestion_dir, "dataset_version.txt")
        self._processing_dir = processing_dir

    def read_dataset_hash(self) -> str | None:
        if not os.path.exists(self._dataset_hash_path):
            return None
        with open(self._dataset_hash_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def read_last_processed_hash(self, dataset: str, model_name: str) -> str | None:
        model_dir = os.path.join(self._processing_dir, model_name)
        summary_path = os.path.join(model_dir, f"{dataset}_model_summary.parquet")
        info_path = os.path.join(model_dir, f"{dataset}_model_info.parquet")

        if os.path.exists(summary_path):
            df = pd.read_parquet(summary_path)
            return self._extract_hash(df)

        if os.path.exists(info_path):
            df = pd.read_parquet(info_path)
            return self._extract_hash(df)

        return None

    def invalidate_model_results(self, dataset: str, model_name: str) -> None:
        model_dir = os.path.join(self._processing_dir, model_name)
        if not os.path.exists(model_dir):
            return

        logger.warning(
            "Invalidating processing results for model=%s dataset=%s",
            model_name,
            dataset,
        )

        for file in os.listdir(model_dir):
            if file.startswith(dataset) and file.endswith(".parquet"):
                os.remove(os.path.join(model_dir, file))
                logger.info("Deleted %s", file)

    def invalidate_mismatched_results(self, dataset: str, current_hash: str) -> None:
        if not os.path.exists(self._processing_dir):
            return

        for entry in os.listdir(self._processing_dir):
            model_dir = os.path.join(self._processing_dir, entry)
            if not os.path.isdir(model_dir):
                continue

            last_hash = self.read_last_processed_hash(dataset, entry)
            if last_hash is None:
                continue

            if last_hash != current_hash:
                logger.warning(
                    "Hash mismatch for model=%s dataset=%s (last=%s current=%s)",
                    entry,
                    dataset,
                    last_hash,
                    current_hash,
                )
                self.invalidate_model_results(dataset, entry)

    @staticmethod
    def _extract_hash(df: pd.DataFrame) -> str | None:
        if df.empty or "dataset_hash" not in df.columns:
            return None

        if "created_at" in df.columns:
            try:
                df_sorted = df.sort_values("created_at", ascending=False)
                return str(df_sorted.iloc[0]["dataset_hash"])
            except Exception:  # noqa: BLE001 - defensive sorting
                return str(df.iloc[0]["dataset_hash"])

        return str(df.iloc[0]["dataset_hash"])
