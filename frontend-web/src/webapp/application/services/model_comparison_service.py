import numpy as np
import pandas as pd


class ModelComparisonService:
    """
    Application service responsible for building comparable, aggregated
    representations of topic modeling results across different models.
    """

    def build_model_summary(
        self,
        model_summary: pd.DataFrame,
        metrics: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build a single-row summary for one model run.
        """
        model_info = model_summary.iloc[0]
        metric_map = metrics.set_index("metric")["value"].to_dict()

        summary = {
            "dataset": str(model_info["dataset"]),
            "model_name": str(model_info["model_name"]),
            "run_id": str(model_info["run_id"]),
            "num_topics": int(model_info["num_topics"]),
            "coherence": float(metric_map.get("coherence", np.nan)),
            "runtime_seconds": float(model_info["runtime_seconds"]),
        }

        return pd.DataFrame([summary])

    def build_topics_representation(
        self, dataset: str, model_summary: pd.DataFrame, topics: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate topic words per topic for semantic comparison.
        """
        model_info = model_summary.iloc[0]
        grouped = (
            topics.sort_values(["topic_id", "rank"])
            .groupby("topic_id")
            .agg(top_words=("word", list))
            .reset_index()
        )

        grouped["dataset"] = dataset
        grouped["model_name"] = str(model_info["model_name"])
        grouped["run_id"] = str(model_info["run_id"])

        return grouped[["dataset", "model_name", "run_id", "topic_id", "top_words"]]

    def build_documents_representation(
        self,
        dataset: str,
        model_summary: pd.DataFrame,
        doc_topics: pd.DataFrame,
        doc_metrics: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build document-topic representation enriched with entropy.
        """

        model_info = model_summary.iloc[0]

        doc_metrics = self._compute_document_metrics(doc_topics)
        merged = doc_topics.merge(doc_metrics, on="document_id", how="left")

        merged["dataset"] = dataset
        merged["model_name"] = str(model_info["model_name"])
        merged["run_id"] = str(model_info["run_id"])

        return merged[
            [
                "dataset",
                "model_name",
                "run_id",
                "document_id",
                "topic_id",
                "probability",
                "entropy",
            ]
        ]

    def build_hyperparams_representation(
        self, dataset: str, model_summary: pd.DataFrame, params: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Return final hyperparameters used by the model run.
        """

        model_info = model_summary.iloc[0]  # 🔑 clave

        params = params.copy()
        params["dataset"] = dataset
        params["model_name"] = str(model_info["model_name"])
        params["run_id"] = str(model_info["run_id"])

        return params[["dataset", "model_name", "run_id", "param", "value"]]

    def compute_final_scores(self, summary_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute a normalized final score for cross-model comparison.
        """

        summary_df = summary_df.copy()

        if len(summary_df) == 1:
            summary_df["final_score"] = 1.0
            return summary_df

        def minmax_norm(series: pd.Series, reverse: bool = False) -> pd.Series:
            series = series.astype(float)
            mn = float(series.min())
            mx = float(series.max())

            if mx == mn:
                return pd.Series(0.0, index=series.index)

            normed = (series - mn) / (mx - mn)
            return 1.0 - normed if reverse else normed

        # Pesos explícitos y positivos
        weights = {
            "coherence": 0.5,
            "runtime_seconds": 0.3,  # penalización suave
        }

        score = pd.Series(0.0, index=summary_df.index)
        total_weight = 0.0

        # Coherence (a maximizar)
        if (
            "coherence" in summary_df.columns
            and not summary_df["coherence"].isna().all()
        ):
            score += weights["coherence"] * minmax_norm(summary_df["coherence"])
            total_weight += weights["coherence"]

        # Runtime (a minimizar → reverse=True)
        if (
            "runtime_seconds" in summary_df.columns
            and not summary_df["runtime_seconds"].isna().all()
        ):
            score += weights["runtime_seconds"] * minmax_norm(
                summary_df["runtime_seconds"], reverse=True
            )
            total_weight += weights["runtime_seconds"]

        # Normalización final por si falta alguna métrica
        if total_weight > 0:
            score /= total_weight

        summary_df["final_score"] = score.clip(0.0, 1.0)

        return summary_df

    @staticmethod
    def _compute_document_metrics(doc_topics: pd.DataFrame) -> pd.DataFrame:
        """
        Compute max probability and entropy per document.
        """

        return (
            doc_topics.groupby("document_id")["probability"]
            .agg(max_prob="max", entropy=lambda p: -(p * np.log(p + 1e-9)).sum())
            .reset_index()
        )
