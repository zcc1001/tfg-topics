import os
from typing import Optional

import pandas as pd

from webapp.application.ports.topic_model_repository import TopicModelRepository


class TopicModelParquetRepository(TopicModelRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def _data_dir(self, model_name: str) -> str:
        return os.path.join(self.base_path, model_name)

    def _path(self, model_name: str, dataset: str, suffix: str) -> str:
        return os.path.join(self._data_dir(model_name), f"{dataset}_{suffix}.parquet")

    def _safe_read(self, path: str) -> Optional[pd.DataFrame]:
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)

    def available_models(self) -> list[str]:
        if not os.path.isdir(self.base_path):
            return []
        return sorted(
            entry
            for entry in os.listdir(self.base_path)
            if os.path.isdir(os.path.join(self.base_path, entry))
        )

    def available_datasets(self) -> list[str]:
        datasets: set[str] = set()
        for model_name in self.available_models():
            model_dir = self._data_dir(model_name)
            for filename in os.listdir(model_dir):
                if filename.endswith("_model_summary.parquet"):
                    datasets.add(filename.removesuffix("_model_summary.parquet"))
        return sorted(datasets)

    def available_models_for_dataset(self, dataset: str) -> list[str]:
        return [
            model_name
            for model_name in self.available_models()
            if self.exists(model_name=model_name, dataset=dataset)
        ]

    def exists(self, model_name: str, dataset: str) -> bool:
        """
        A model is considered available if the minimal required files exist.
        """
        required_files = [
            self._path(model_name, dataset, "model_summary"),
            self._path(model_name, dataset, "metrics"),
            self._path(model_name, dataset, "document_topics"),
        ]
        return all(os.path.exists(p) for p in required_files)

    def load_model_info(self, model_name: str, dataset: str) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "model_summary"))

    def load_topics(self, model_name: str, dataset: str) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "topics"))

    def load_document_topics(
        self, model_name: str, dataset: str
    ) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "document_topics"))

    def load_metrics(self, model_name: str, dataset: str) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "metrics"))

    def load_params(self, model_name: str, dataset: str) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "params"))

    def load_topic_coordinates(
        self, model_name: str, dataset: str
    ) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "topic_coordinates"))

    def load_best_hyperparams(
        self, model_name: str, dataset: str
    ) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "best_hyperparameters"))

    def load_hyperparams_trials(
        self, model_name: str, dataset: str
    ) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path(model_name, dataset, "hyperparameter_trials"))
