import pandas as pd
import streamlit as st

from webapp.application.usecases.load_model_results_usecase import (
    LoadModelResultsUseCase,
)
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.page_header import render_page_header
from webapp.ui.components.persistent_widgets import persistent_selectbox
from webapp.ui.components.render_intertopic_distance_map import (
    render_intertopic_distance_map,
)
from webapp.ui.components.render_topic_summary_table import render_topic_summary_table
from webapp.ui.components.section_scroll import render_section_anchor, scroll_to_section
from webapp.ui.components.wordcloud import render_wordcloud
from webapp.ui.i18n import _

DEFAULT_DATASETS = ["issues", "readmes", "thesis", "abstracts"]
DEFAULT_MODELS = ["lda", "bertopic", "fastopic", "top2vec"]


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


def render_model_analysis(base_dir: str, selected_section: str | None = None) -> None:
    """Render the topic model .

    Args:
        base_dir (str): directory where the model results are stored.
    """
    render_page_header(
        page_title=_("model.title"),
        description=_("model.desc"),
    )
    repository = TopicModelParquetRepository(base_path=base_dir)
    datasets = repository.available_datasets() or DEFAULT_DATASETS
    section_key = (selected_section or "default").lower().replace(" ", "_")

    left, middle = st.columns(2, vertical_alignment="bottom")
    with left:
        dataset = persistent_selectbox(
            label=_("common.select_dataset"),
            options=datasets,
            state_key="model_analysis_selected_dataset",
            widget_key=f"model_analysis_dataset_widget_{section_key}",
            placeholder=_("common.select_origin"),
        )

    available_models = repository.available_models_for_dataset(dataset)
    model_options = available_models or repository.available_models() or DEFAULT_MODELS
    with middle:
        model_name = persistent_selectbox(
            label=_("common.select_model"),
            options=model_options,
            state_key="model_analysis_selected_model",
            widget_key=f"model_analysis_model_widget_{section_key}",
            placeholder=_("common.select_model_placeholder"),
        )

    if dataset and model_name:
        use_case = LoadModelResultsUseCase(repository=repository)
        data = use_case.execute(dataset=dataset, model_name=model_name)
        if data is None or data.get("topics") is None:
            st.warning(
                _("common.no_results_model").format(
                    model_name=model_name, dataset=dataset
                )
            )
            return

        section_anchors = {
            str(_("model.summary")): "model-resumen-ejecutivo",
            str(_("model.exploration")): "model-exploracion-topicos",
            str(_("model.map")): "model-mapa-intertopico",
        }

        render_section_anchor(section_anchors[str(_("model.summary"))])
        st.subheader(f"📊 {_('model.summary')}")

        col1, col2, col3, _dummy = st.columns(4)

        col1.metric(_("model.detected_topics"), _count_detected_topics(data["topics"]))
        col2.metric(
            _("model.analyzed_docs"),
            _count_analyzed_documents(data["document_topics"]),
        )
        col3.metric(_("model.coherence"), round(data["best_params"]["best_score"], 3))

        dominant_topic = _compute_dominant_topic(data["document_topics"])
        if dominant_topic is not None:
            top_topic, dominance_share = dominant_topic
            if dominance_share >= 0.35:
                st.success(
                    _("model.dominant_topic").format(
                        topic=top_topic, share=f"{dominance_share:.1%}"
                    )
                )
            else:
                st.info(
                    _("model.balanced_topic").format(
                        topic=top_topic, share=f"{dominance_share:.1%}"
                    )
                )

        render_section_anchor(section_anchors[str(_("model.exploration"))])
        st.subheader(f"🧠 {_('model.exploration')}")

        tab1, tab2 = st.tabs([f"📋 {_('model.table')}", f"☁️ {_('model.wordcloud')}"])

        with tab1:
            render_topic_summary_table(
                data["topics"],
                max_words=10,
            )

        with tab2:
            render_wordcloud(data["topics"], max_topics_to_render=6)

        render_section_anchor(section_anchors[str(_("model.map"))])
        st.subheader(f"🗺️ {_('model.map')}")
        render_intertopic_distance_map(data["topic_coordinates"])

        if selected_section:
            scroll_to_section(section_anchors.get(selected_section))


if __name__ == "__main__":
    st.set_page_config(page_title="TFG – Analisis de modelos", layout="wide")
    processing_dir = st.session_state.processing_dir
    render_model_analysis(processing_dir)
