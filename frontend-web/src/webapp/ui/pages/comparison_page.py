import pandas as pd
import streamlit as st

from webapp.application.services.model_comparison_service import ModelComparisonService
from webapp.application.usecases.compare_models_usecase import CompareModelsUseCase
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)


def render_comparison(base_dir: str) -> None:
    """Render the model comparison page.
    Args:
        base_dir (str): directory where the model results are stored.
    """
    st.set_page_config(page_title="TFG – Comparación de modelos", layout="wide")
    st.title("TFG Topics")
    st.divider()
    st.header("Comparativa de modelos")

    dataset = st.selectbox(
        "Selecciona un dataset", ["issues", "readmes", "thesis", "abstracts"]
    )

    models = st.multiselect(
        "Selecciona modelos a comparar",
        ["lda", "bertopic", "fastopic", "top2vec"],
        default=["lda", "bertopic", "fastopic", "top2vec"],
    )

    if not models:
        st.info("Selecciona al menos un modelo.")
        return

    runs = [{"dataset": dataset, "model_name": model} for model in models]

    with st.spinner("Cargando modelos..."):
        use_case = CompareModelsUseCase(
            service=ModelComparisonService(),
            repository=TopicModelParquetRepository(base_path=base_dir),
        )

        results = use_case.execute(runs)
        skipped = results["skipped"]["model_name"].tolist()
        if skipped:
            st.warning(f"No hay resultados disponibles para: {', '.join(skipped)}")

        summary_df = results["summary"]

        if summary_df.empty:
            st.info("No hay modelos disponibles para este dataset.")
            return

        _render_summary(summary_df)
        _render_metrics(summary_df)


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

    st.subheader("Ranking global")
    st.caption(
        "Ranking relativo entre los modelos seleccionados para el dataset actual."
    )
    st.bar_chart(
        summary_df.sort_values("final_score", ascending=False).set_index("model_name")[
            "final_score"
        ]
    )


def _render_metrics(summary_df: pd.DataFrame) -> None:
    st.subheader("Comparación de métricas")

    metric = st.selectbox(
        "Métrica",
        [
            "coherence",
            "runtime_seconds",
        ],
    )

    st.bar_chart(summary_df.set_index("model_name")[metric])


if __name__ == "__main__":
    processing_dir = st.session_state.processing_dir
    render_comparison(processing_dir)
