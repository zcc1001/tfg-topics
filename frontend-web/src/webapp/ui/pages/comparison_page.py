import pandas as pd
import streamlit as st

from webapp.application.services.model_comparison_service import ModelComparisonService
from webapp.application.usecases.compare_models_usecase import CompareModelsUseCase
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.page_header import render_page_header
from webapp.ui.components.persistent_widgets import (
    persistent_multiselect,
    persistent_selectbox,
)
from webapp.ui.components.section_scroll import render_section_anchor, scroll_to_section

DEFAULT_DATASETS = ["issues", "readmes", "thesis", "abstracts"]
DEFAULT_MODELS = ["lda", "bertopic", "fastopic", "top2vec"]


def render_comparison(base_dir: str, selected_section: str | None = None) -> None:
    """Render the model comparison page.
    Args:
        base_dir (str): directory where the model results are stored.
    """
    render_page_header(page_title="Comparativa de modelos")

    repository = TopicModelParquetRepository(base_path=base_dir)
    datasets = repository.available_datasets() or DEFAULT_DATASETS
    section_key = (selected_section or "default").lower().replace(" ", "_")
    dataset = persistent_selectbox(
        label="Selecciona un dataset",
        options=datasets,
        state_key="comparison_selected_dataset",
        widget_key=f"comparison_dataset_widget_{section_key}",
    )

    available_models = repository.available_models_for_dataset(dataset)
    model_options = available_models or repository.available_models() or DEFAULT_MODELS
    models = persistent_multiselect(
        label="Selecciona modelos a comparar",
        options=model_options,
        state_key="comparison_selected_models",
        widget_key=f"comparison_models_widget_{section_key}",
    )

    if not models:
        st.info("Selecciona al menos un modelo.")
        return

    runs = [{"dataset": dataset, "model_name": model} for model in models]

    with st.spinner("Cargando modelos..."):
        use_case = CompareModelsUseCase(
            service=ModelComparisonService(),
            repository=repository,
        )

        results = use_case.execute(runs)
        skipped = results["skipped"]["model_name"].tolist()
        if skipped:
            st.warning(f"No hay resultados disponibles para: {', '.join(skipped)}")

        summary_df = results["summary"]

        if summary_df.empty:
            st.info("No hay modelos disponibles para este dataset.")
            return

        section_anchors = {
            "Resumen comparativo": "comparison-resumen",
            "Ranking global": "comparison-ranking",
            "Comparación de métricas": "comparison-metricas",
        }

        render_section_anchor(section_anchors["Resumen comparativo"])
        _render_summary(summary_df)

        render_section_anchor(section_anchors["Ranking global"])
        _render_ranking(summary_df)

        render_section_anchor(section_anchors["Comparación de métricas"])
        _render_metrics(summary_df, section_key=section_key)

        if selected_section:
            scroll_to_section(section_anchors.get(selected_section))


def _render_summary(summary_df: pd.DataFrame) -> None:
    st.subheader("Resumen comparativo")

    st.dataframe(
        summary_df.sort_values("final_score", ascending=False), use_container_width=True
    )

    st.caption(
        "El score final combina coherencia, tiempo de ejecución "
        ", normalizados entre modelos disponibles."
    )

    best = summary_df.sort_values("final_score", ascending=False).iloc[0]
    st.success(
        f"Modelo recomendado: **{best['model_name']}** "
        f"(score = {best['final_score']:.2f})"
    )


def _render_ranking(summary_df: pd.DataFrame) -> None:
    st.subheader("Ranking global")
    st.caption(
        "Ranking relativo entre los modelos seleccionados para el dataset actual."
    )
    st.bar_chart(
        summary_df.sort_values("final_score", ascending=False).set_index("model_name")[
            "final_score"
        ]
    )


def _render_metrics(summary_df: pd.DataFrame, section_key: str = "default") -> None:
    st.subheader("Comparación de métricas")

    metric = persistent_selectbox(
        label="Métrica",
        options=[
            "coherence",
            "runtime_seconds",
        ],
        state_key="comparison_selected_metric",
        widget_key=f"comparison_metric_widget_{section_key}",
    )

    st.bar_chart(summary_df.set_index("model_name")[metric])


if __name__ == "__main__":
    st.set_page_config(page_title="TFG – Comparación de modelos", layout="wide")
    processing_dir = st.session_state.processing_dir
    render_comparison(processing_dir)
