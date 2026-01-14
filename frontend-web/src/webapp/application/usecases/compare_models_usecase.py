from typing import Dict, List

import pandas as pd

from webapp.application.ports.topic_model_repository import TopicModelRepository
from webapp.application.services.model_comparison_service import ModelComparisonService


class CompareModelsUseCase:
    """
    Use case responsible for comparing multiple topic models
    over the same dataset using precomputed Parquet results.
    """

    def __init__(
        self, service: ModelComparisonService, repository: TopicModelRepository
    ):
        self._service = service
        self._repository = repository

    def execute(self, runs: List[Dict]) -> Dict[str, pd.DataFrame]:
        """
        Execute model comparison.

        Args:
            runs (List[Dict]): List of runs to compare.
                Each run must contain:
                    - dataset (str)
                    - model_name (str)

        Returns:
            Dict[str, pd.DataFrame]: Aggregated results ready for visualization.
        """

        summaries = []
        topics = []
        documents = []
        params = []
        skipped_models = pd.DataFrame(columns=["model_name"])
        for run in runs:
            dataset = run["dataset"]
            model_name = run["model_name"]

            if not self._repository.exists(model_name, dataset):
                new_row = pd.DataFrame({"model_name": [model_name]})
                skipped_models = pd.concat([skipped_models, new_row], ignore_index=True)
                continue

            model_summary_opt = self._repository.load_model_info(
                model_name=model_name, dataset=dataset
            )
            metrics_opt = self._repository.load_metrics(
                model_name=model_name, dataset=dataset
            )
            document_topics_opt = self._repository.load_document_topics(
                model_name=model_name, dataset=dataset
            )
            topics_opt = self._repository.load_topics(
                model_name=model_name, dataset=dataset
            )
            params_opt = self._repository.load_params(
                model_name=model_name, dataset=dataset
            )
            coordinates_opt = self._repository.load_topic_coordinates(
                model_name=model_name, dataset=dataset
            )

            # Defensive check (por si falta algo inesperado)
            if any(
                df is None
                for df in [
                    model_summary_opt,
                    metrics_opt,
                    document_topics_opt,
                    topics_opt,
                    params_opt,
                    coordinates_opt,
                ]
            ):
                new_row = pd.DataFrame({"model_name": [model_name]})
                skipped_models = pd.concat([skipped_models, new_row], ignore_index=True)
                continue

            assert model_summary_opt is not None
            assert metrics_opt is not None
            assert document_topics_opt is not None
            assert topics_opt is not None
            assert params_opt is not None
            assert coordinates_opt is not None

            model_summary: pd.DataFrame = model_summary_opt
            metrics: pd.DataFrame = metrics_opt
            document_topics: pd.DataFrame = document_topics_opt
            topics_df: pd.DataFrame = topics_opt
            params_df: pd.DataFrame = params_opt

            summaries.append(
                self._service.build_model_summary(
                    model_summary=model_summary,
                    metrics=metrics,
                )
            )

            topics.append(
                self._service.build_topics_representation(
                    dataset=dataset,
                    model_summary=model_summary,
                    topics=topics_df,
                )
            )

            documents.append(
                self._service.build_documents_representation(
                    dataset=dataset,
                    model_summary=model_summary,
                    doc_topics=document_topics,
                    doc_metrics=metrics,
                )
            )

            params.append(
                self._service.build_hyperparams_representation(
                    dataset=dataset,
                    model_summary=model_summary,
                    params=params_df,
                )
            )

        if not summaries:
            return {
                "summary": pd.DataFrame(),
                "topics": pd.DataFrame(),
                "documents": pd.DataFrame(),
                "params": pd.DataFrame(),
                "skipped": skipped_models,
            }

        summary_df = pd.concat(summaries, ignore_index=True)
        summary_df = self._service.compute_final_scores(summary_df)

        return {
            "summary": summary_df,
            "topics": pd.concat(topics, ignore_index=True),
            "documents": pd.concat(documents, ignore_index=True),
            "params": pd.concat(params, ignore_index=True),
            "skipped": skipped_models,
        }
