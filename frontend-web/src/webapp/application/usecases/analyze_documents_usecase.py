import logging
from typing import Dict, Optional, Tuple

import pandas as pd

from webapp.application.ports.metadata_repository import MetadataRepository
from webapp.application.ports.topic_model_repository import TopicModelRepository

logger = logging.getLogger(__name__)


class AnalyzeDocumentsUseCase:
    """
    Academic-oriented analysis of documents enriched with topic modeling.
    Topic labels are generated from the 5 most representative words per topic.
    """

    def __init__(
        self, topic_repo: TopicModelRepository, metadata_repo: MetadataRepository
    ):
        self.topic_repo = topic_repo
        self.metadata_repo = metadata_repo

    def execute(
        self,
        dataset: str,
        model_name: str,
        tutor: Optional[str] = None,
        year: Optional[int] = None,
        grade_range: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, pd.DataFrame]:
        docs = self.topic_repo.load_document_topics(
            dataset=dataset, model_name=model_name
        )
        if docs is None or docs.empty:
            raise ValueError("Documents not found")

        docs = self._normalize_document_identifiers(docs)
        metadata = self.metadata_repo.load_dataset_metadata(dataset)
        metadata = self._normalize_metadata(metadata)
        df = self._merge_documents_with_metadata(docs, metadata)
        df = self._ensure_optional_columns(df)

        df = self._add_grade_category(df)
        df = self._prepare_grouping_fields(df)

        df = self._apply_filters(df, tutor, year, grade_range)

        df = df.sort_values("probability", ascending=False)
        df = df.groupby("document_id").head(1)

        documents_summary = self._build_document_summary(df)
        topic_distribution = self._build_topic_distribution(df)
        topic_distribution = self._enhance_topic_distribution(topic_distribution)

        topic_words = self._load_topic_words(dataset, model_name)
        topic_labels = self._build_topic_labels(topic_words)

        top_topics_by_grade = self._build_top_topics_by_grade(df)

        return {
            "documents_raw": df,
            "documents_summary": documents_summary,
            "topic_distribution": topic_distribution,
            "topics": topic_labels,
            "top_topics_by_grade": top_topics_by_grade,
        }

    def _normalize_document_identifiers(self, docs: pd.DataFrame) -> pd.DataFrame:
        df = docs.copy()

        # Topic modeling stores an internal row index as document_id for some
        # datasets. We promote meta_thesis_id to the canonical ID so frontend
        # joins use the academic thesis identifier that matches metadata.parquet.
        if "meta_thesis_id" in df.columns:
            if "document_id" in df.columns:
                df = df.rename(columns={"document_id": "topic_document_id"})
            df = df.rename(columns={"meta_thesis_id": "document_id"})

        rename_map = {
            "thesis_id": "document_id",
            "doc_id": "document_id",
        }

        for source, target in rename_map.items():
            if source in df.columns and target not in df.columns:
                df = df.rename(columns={source: target})

        if "document_id" not in df.columns:
            raise ValueError("Document id not found in document topics")

        return df

    def _normalize_metadata(self, metadata: Optional[pd.DataFrame]) -> pd.DataFrame:
        if metadata is None or metadata.empty:
            return pd.DataFrame()

        df = metadata.copy()
        rename_map = {
            "thesis_id": "document_id",
            "doc_id": "document_id",
            "name": "title",
        }

        applicable_renames = {
            source: target
            for source, target in rename_map.items()
            if source in df.columns and target not in df.columns
        }
        if applicable_renames:
            df = df.rename(columns=applicable_renames)

        return df

    def _merge_documents_with_metadata(
        self, docs: pd.DataFrame, metadata: pd.DataFrame
    ) -> pd.DataFrame:
        # Document analysis depends on academic metadata such as title, tutor,
        # year, and grade. If that metadata is missing, the analysis would show
        # incomplete results, so we fail fast instead of silently degrading.
        if metadata.empty or "document_id" not in metadata.columns:
            raise ValueError("Metadata not found for document analysis")

        # Only keep documents that have a real metadata match. This enforces the
        # business rule that every analyzed document must be traceable to a
        # canonical metadata record.
        merged = docs.merge(
            metadata,
            on="document_id",
            how="inner",
        )

        dropped_documents = (
            docs["document_id"].nunique() - merged["document_id"].nunique()
        )
        if dropped_documents > 0:
            logger.warning(
                "Dropped %s documents without matching metadata",
                dropped_documents,
            )

        return merged

    def _ensure_optional_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        fallback_columns: dict[str, list[str]] = {
            "title": ["document", "text", "content", "body"],
            "tutor": [],
            "year": [],
            "grade": [],
        }

        for target, candidates in fallback_columns.items():
            if target in normalized.columns:
                continue

            fallback_series = None
            for candidate in candidates:
                if candidate in normalized.columns:
                    fallback_series = normalized[candidate]
                    break

            if fallback_series is None:
                fallback_series = pd.Series([pd.NA] * len(normalized))

            normalized[target] = fallback_series

        return normalized

    def _apply_filters(
        self,
        df: pd.DataFrame,
        tutor: Optional[str],
        year: Optional[int],
        grade_range: Optional[Tuple[float, float]],
    ) -> pd.DataFrame:

        df = df.copy()

        if tutor and tutor != "Todos" and "tutor" in df.columns:
            tutor_clean = tutor.strip().lower()
            df = df[
                df["tutor"]
                .fillna("")
                .str.lower()
                .str.contains(tutor_clean, regex=False)
            ]

        if year and year != "Todos" and "year" in df.columns:
            df = df[df["year"] == year]

        if grade_range and grade_range != (0.0, 10.0) and "grade" in df.columns:
            min_grade, max_grade = grade_range
            df["grade"] = pd.to_numeric(df["grade"], errors="coerce")
            df = df[(df["grade"] >= min_grade) & (df["grade"] <= max_grade)]

        return df

    def _add_grade_category(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        grades_series = df.get("grade")
        if grades_series is None:
            grades_series = pd.Series([pd.NA] * len(df))
        grades = pd.to_numeric(grades_series, errors="coerce")

        bins = [-float("inf"), 5, 7, 9, 10.1]
        labels = [
            "Suspenso (<5)",
            "Aprobado (5–6.9)",
            "Notable (7–8.9)",
            "Sobresaliente (9–10)",
        ]

        df["grade_category"] = pd.cut(
            grades, bins=bins, labels=labels, include_lowest=True
        )
        df["grade_category"] = df["grade_category"].astype(str)
        df.loc[grades.isna(), "grade_category"] = "Sin calificación"
        return df

    def _prepare_grouping_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["tutor_group"] = df["tutor"].fillna("Sin tutor").astype(str)
        df["year_group"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        df["year_group"] = df["year_group"].astype(str)
        df.loc[df["year_group"] == "<NA>", "year_group"] = "Sin año"
        return df

    def _build_document_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        grade_series = pd.to_numeric(df.get("grade"), errors="coerce")
        return (
            df[
                [
                    "document_id",
                    "title",
                    "tutor_group",
                    "year_group",
                    "grade_category",
                    "topic_id",
                    "probability",
                ]
            ]
            .assign(grade=grade_series)
            .rename(
                columns={
                    "topic_id": "tópico_principal",
                    "probability": "peso_del_tópico",
                }
            )
        )

    def _build_topic_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(
                ["tutor_group", "year_group", "grade_category", "topic_id"],
                dropna=False,
            )
            .agg(
                documentos=("document_id", "nunique"),
                peso_total=("probability", "sum"),
            )
            .reset_index()
        )

    def _enhance_topic_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["peso_medio_por_documento"] = (df["peso_total"] / df["documentos"]).round(3)

        df["relevancia"] = pd.cut(
            df["peso_medio_por_documento"],
            bins=[0, 0.25, 0.5, 0.75, 1.1],
            labels=["Baja", "Media", "Alta", "Muy alta"],
            include_lowest=True,
        )
        return df

    def _load_topic_words(self, dataset: str, model_name: str) -> pd.DataFrame:
        topics = self.topic_repo.load_topics(dataset=dataset, model_name=model_name)

        if topics is None or topics.empty:
            logger.warning("No topic-word data available for model %s", model_name)
            return pd.DataFrame(columns=["topic_id", "palabras_clave"])

        # LDA clásico
        if {"topic_id", "word"}.issubset(topics.columns):
            if "rank" in topics.columns:
                topics = topics.sort_values(["topic_id", "rank"])
            return (
                topics.groupby("topic_id")["word"]
                .apply(lambda s: ", ".join(s.tolist()))
                .reset_index(name="palabras_clave")
            )

        # BERTopic / Fastopic
        if {"topic_id", "term"}.issubset(topics.columns):
            return (
                topics.groupby("topic_id")["term"]
                .apply(lambda s: ", ".join(s.tolist()))
                .reset_index(name="palabras_clave")
            )

        logger.warning(
            "Unknown topic-word schema for model %s: %s",
            model_name,
            list(topics.columns),
        )

        return pd.DataFrame(columns=["topic_id", "palabras_clave"])

    def _build_topic_labels(self, topics: pd.DataFrame) -> pd.DataFrame:
        """
        Generates topic labels using the 5 most representative words
        and includes the topic number in the visual label.
        """
        if topics.empty:
            return pd.DataFrame(
                columns=["topic_id", "etiqueta_tópico", "palabras_clave"]
            )

        df = topics.copy()

        df["topic_id"] = df["topic_id"].astype(int)

        df["etiqueta_tópico"] = df.apply(
            lambda row: (
                f"T{row['topic_id']} · "
                + ", ".join(row["palabras_clave"].split(", ")[:5])
                if isinstance(row["palabras_clave"], str)
                else f"T{row['topic_id']}"
            ),
            axis=1,
        )

        return df[["topic_id", "etiqueta_tópico", "palabras_clave"]]

    def _build_top_topics_by_grade(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(["grade_category", "topic_id"])
            .agg(
                documentos=("document_id", "nunique"),
                peso_total=("probability", "sum"),
            )
            .reset_index()
            .sort_values(["grade_category", "peso_total"], ascending=[True, False])
        )
