import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from processing.application.ports.storage_port import StoragePort
from processing.domain.entities import HyperparameterSearchResult, TopicModelResult

logger = logging.getLogger(__name__)


class DataParquetStorageWriter(StoragePort):
    def __init__(
        self,
        processing_data_dir: str = "data",
        results_filename: str = "results.parquet",
        buffer_size: int = 500,
        compression: str = "snappy",
    ):
        os.makedirs(processing_data_dir, exist_ok=True)
        self.processing_data_dir = processing_data_dir
        self.results_filename = results_filename
        self.buffer_size = int(buffer_size)
        self.compression = compression

    def write_hyperparameter_search(
        self,
        result: HyperparameterSearchResult,
    ) -> None:
        logger.info(
            "Writing hyperparameter search results to %s", self.processing_data_dir
        )

        os.makedirs(self.processing_data_dir, exist_ok=True)
        result_dir = os.path.join(self.processing_data_dir, result.model_name)
        logger.info("Writing topic model results to %s", result_dir)

        os.makedirs(result_dir, exist_ok=True)

        trials_rows: List[Dict[str, Any]] = []

        for trial in result.trials:
            row = {
                "trial_id": trial.trial_id,
                "model": trial.model_name,
                "score": trial.score,
                "state": trial.state,
            }
            row.update(trial.params)
            trials_rows.append(row)

        trials_df = pd.DataFrame(trials_rows)
        trials_output_path = os.path.join(
            result_dir, result.source + "_hyperparameter_trials.parquet"
        )
        trials_df.to_parquet(
            trials_output_path,
            index=False,
        )
        logger.info("Hyperparameter trials saved to %s", trials_output_path)

        best_df = pd.DataFrame(
            [
                {
                    "model": result.model_name,
                    "best_score": result.best_score,
                    **result.best_params,
                }
            ]
        )

        best_output_path = os.path.join(
            result_dir, result.source + "_best_hyperparameters.parquet"
        )
        best_df.to_parquet(
            best_output_path,
            index=False,
        )
        logger.info("Best hyperparameters saved to %s", best_output_path)
        logger.info("Finished writing hyperparameter search results")

    def write_topic_model_result(
        self,
        run_id: str,
        result: TopicModelResult,
    ) -> None:
        os.makedirs(self.processing_data_dir, exist_ok=True)
        result_dir = os.path.join(self.processing_data_dir, result.model_name)
        logger.info("Writing topic model results to %s", result_dir)
        os.makedirs(result_dir, exist_ok=True)

        self._write_model_info(result_dir, result, run_id)
        self._write_topics(result_dir, result, run_id)
        self._write_document_topics(result_dir, result, run_id)
        self._write_metrics(result_dir, result, run_id)
        self._write_params(result_dir, result, run_id)
        self._write_topic_coordinates(result_dir, result, run_id)

    def _write_model_info(
        self,
        result_dir: str,
        result: TopicModelResult,
        run_id: str,
    ) -> None:
        df = pd.DataFrame(
            [
                {
                    "model_name": result.model_name,
                    "model_type": result.model_name.lower(),
                    "run_id": run_id,
                    "created_at": datetime.now(timezone.utc),
                    "num_topics": len(result.topics),
                }
            ]
        )
        df.to_parquet(
            os.path.join(result_dir, result.source + "_model_info.parquet"), index=False
        )

    def _write_topics(
        self, result_dir: str, result: TopicModelResult, run_id: str
    ) -> None:
        rows = []

        for topic_id, words in result.topics.items():
            for rank, word in enumerate(words, start=1):
                rows.append(
                    {
                        "model_name": result.model_name,
                        "run_id": run_id,
                        "topic_id": topic_id,
                        "word": word,
                        "weight": None,
                        "rank": rank,
                    }
                )

        df = pd.DataFrame(rows)
        df.to_parquet(
            os.path.join(result_dir, result.source + "_topics.parquet"), index=False
        )

    def _write_document_topics(
        self, result_dir: str, result: TopicModelResult, run_id: str
    ) -> None:
        df = pd.DataFrame(result.document_topics)

        if not df.empty:
            df["model_name"] = result.model_name
            df["run_id"] = run_id
        df.to_parquet(
            os.path.join(result_dir, result.source + "_document_topics.parquet"),
            index=False,
        )

    def _write_metrics(
        self, result_dir: str, result: TopicModelResult, run_id: str
    ) -> None:
        rows = []

        for metric, value in result.metrics.items():
            rows.append(
                {
                    "model_name": result.model_name,
                    "run_id": run_id,
                    "metric": metric,
                    "value": value,
                }
            )

        df = pd.DataFrame(rows)
        df.to_parquet(
            os.path.join(result_dir, result.source + "_metrics.parquet"), index=False
        )

    def _write_params(
        self, result_dir: str, result: TopicModelResult, run_id: str
    ) -> None:
        rows = []

        for param, value in result.params.items():
            rows.append(
                {
                    "model_name": result.model_name,
                    "run_id": run_id,
                    "param": param,
                    "value": value,
                }
            )

        df = pd.DataFrame(rows)
        df["value"] = df["value"].astype(str)
        df.to_parquet(
            os.path.join(result_dir, result.source + "_params.parquet"), index=False
        )

    def _write_topic_coordinates(
        self, result_dir: str, result: TopicModelResult, run_id: str
    ) -> None:
        df = pd.DataFrame(result.topic_coordinates)
        df["model_name"] = result.model_name
        df["run_id"] = run_id

        df.to_parquet(
            os.path.join(result_dir, result.source + "_topic_coordinates.parquet"),
            index=False,
        )
