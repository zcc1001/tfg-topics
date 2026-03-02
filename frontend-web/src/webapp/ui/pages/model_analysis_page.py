import pandas as pd
import streamlit as st

from webapp.application.usecases.load_model_results_usecase import (
    LoadModelResultsUseCase,
)
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.render_intertopic_distance_map import (
    render_intertopic_distance_map,
)
from webapp.ui.components.render_topic_summary_table import render_topic_summary_table
from webapp.ui.components.wordcloud import render_wordcloud


def _count_detected_topics(topics_df: pd.DataFrame) -> int:
    """Count detected topics from topic rows, excluding outlier topic -1."""
    if topics_df.empty or "topic_id" not in topics_df.columns:
        return 0

    topic_ids = pd.to_numeric(topics_df["topic_id"], errors="coerce").dropna()
    return int(topic_ids[topic_ids >= 0].nunique())


def _count_analyzed_documents(document_topics_df: pd.DataFrame) -> int:
    """Count unique analyzed documents, excluding missing document ids."""
    if document_topics_df.empty or "document_id" not in document_topics_df.columns:
        return 0

    return int(document_topics_df["document_id"].nunique(dropna=True))


def _compute_dominant_topic(
    document_topics_df: pd.DataFrame,
) -> tuple[int, float] | None:
    """Return dominant topic id and its share based on probability mass."""
    if document_topics_df.empty or "topic_id" not in document_topics_df.columns:
        return None

    df = document_topics_df.copy()
    df["topic_id"] = pd.to_numeric(df["topic_id"], errors="coerce")
    df = df[df["topic_id"].notna() & (df["topic_id"] >= 0)]
    if df.empty:
        return None

    if "probability" in df.columns:
        df["probability"] = pd.to_numeric(df["probability"], errors="coerce")
        weight_by_topic = df.groupby("topic_id")["probability"].sum(min_count=1)
    else:
        weight_by_topic = df.groupby("topic_id").size().astype(float)

    weight_by_topic = weight_by_topic.dropna()
    if weight_by_topic.empty:
        return None

    top_topic = int(weight_by_topic.idxmax())
    total_weight = float(weight_by_topic.sum())
    dominance_share = float(weight_by_topic.loc[top_topic] / total_weight)
    return top_topic, dominance_share


def render_model_analysis(base_dir: str) -> None:
    """Render the topic model .

    Args:
        base_dir (str): directory where the model results are stored.
    """
    st.set_page_config(page_title="TFG – Analisis de modelos", layout="wide")
    st.title("TFG Topics")
    st.divider()
    st.header("Análisis por modelo")

    st.caption(
        "Selecciona el conjunto de documentos y el modelo de tópicos para analizar "
        "sus resultados precomputados."
    )
    with st.form("model_source_form"):
        left, middle, right = st.columns(3, vertical_alignment="bottom")
        dataset = left.selectbox(
            "Selecciona un dataset",
            ["issues", "readmes", "thesis", "abstracts"],
            placeholder="Selecciona un origen...",
        )
        model_name = middle.selectbox(
            "Selecciona un modelo",
            ["lda", "bertopic", "fastopic", "top2vec"],
            placeholder="Selecciona un modelo...",
        )
        right.form_submit_button("Cargar resultados")

    if dataset and model_name:
        use_case = LoadModelResultsUseCase(
            repository=TopicModelParquetRepository(base_path=base_dir)
        )
        data = use_case.execute(dataset=dataset, model_name=model_name)
        if data is None or data.get("topics") is None:
            st.warning(
                f"No hay resultados disponibles para el modelo '{model_name}' "
                f"en el dataset '{dataset}'."
            )
            return

        st.subheader("📊 Resumen ejecutivo")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Tópicos detectados", _count_detected_topics(data["topics"]))
        col2.metric(
            "Documentos analizados",
            _count_analyzed_documents(data["document_topics"]),
        )
        col3.metric("Coherencia", round(data["best_params"]["best_score"], 3))

        dominant_topic = _compute_dominant_topic(data["document_topics"])
        if dominant_topic is not None:
            top_topic, dominance_share = dominant_topic
            if dominance_share >= 0.35:
                st.success(
                    f"El tópico más dominante del modelo es **T{top_topic}** "
                    f"({dominance_share:.1%} del peso temático)."
                )
            else:
                st.info(
                    f"El tópico con mayor peso es **T{top_topic}** "
                    f"({dominance_share:.1%}), con distribución temática equilibrada."
                )

        st.subheader("🧠 Exploración de tópicos")

        tab1, tab2 = st.tabs(["📋 Tabla de tópicos", "☁️ Wordcloud"])

        with tab1:
            render_topic_summary_table(
                data["topics"],
                max_words=10,
            )

        with tab2:
            render_wordcloud(data["topics"], max_topics_to_render=6)

        render_intertopic_distance_map(data["topic_coordinates"])


if __name__ == "__main__":
    processing_dir = st.session_state.processing_dir
    render_model_analysis(processing_dir)
