import pandas as pd
import streamlit as st

from webapp.application.usecases.load_model_results_usecase import (
    LoadModelResultsUseCase,
)
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.best_params_summary import render_best_params_summary
from webapp.ui.components.page_header import render_page_header
from webapp.ui.components.param_vs_score import render_param_vs_score
from webapp.ui.components.persistent_widgets import persistent_selectbox
from webapp.ui.components.section_scroll import render_section_anchor, scroll_to_section
from webapp.ui.components.trial_score_evolution import render_trial_score_evolution

DEFAULT_DATASETS = ["issues", "readmes", "thesis", "abstracts"]
DEFAULT_MODELS = ["lda", "bertopic", "fastopic", "top2vec"]


def render_hyperparameter_analysis(
    base_dir: str, selected_section: str | None = None
) -> None:
    render_page_header(
        page_title="Hiperparametrización del modelo",
        description=(
            "Explora el proceso de búsqueda de hiperparámetros "
            "y su impacto en la calidad del modelo."
        ),
    )

    repository = TopicModelParquetRepository(base_path=base_dir)
    datasets = repository.available_datasets() or DEFAULT_DATASETS
    section_key = (selected_section or "default").lower().replace(" ", "_")

    left, middle = st.columns(2, vertical_alignment="bottom")

    with left:
        dataset = persistent_selectbox(
            label="Dataset",
            options=datasets,
            state_key="hyper_selected_dataset",
            widget_key=f"hyper_dataset_widget_{section_key}",
        )

    model_options = (
        repository.available_models_for_dataset(dataset)
        or repository.available_models()
        or DEFAULT_MODELS
    )
    with middle:
        model_name = persistent_selectbox(
            label="Modelo",
            options=model_options,
            state_key="hyper_selected_model",
            widget_key=f"hyper_model_widget_{section_key}",
        )

    use_case = LoadModelResultsUseCase(repository=repository)

    data = use_case.execute(dataset=dataset, model_name=model_name)

    if data is None:
        st.warning("No hay resultados disponibles.")
        return

    trials_df: pd.DataFrame = data.get("trials")
    best_params_df: pd.DataFrame = data.get("best_params")

    if trials_df is None or trials_df.empty:
        st.warning("No hay datos de búsqueda de hiperparámetros.")
        return

    section_anchors = {
        "Evolución del score": "hyper-evolucion-score",
        "Parámetros vs rendimiento": "hyper-parametros-rendimiento",
        "Mejores hiperparámetros": "hyper-mejores-parametros",
    }

    render_section_anchor(section_anchors["Evolución del score"])
    st.subheader("📈 Evolución del score")
    render_trial_score_evolution(trials_df)

    render_section_anchor(section_anchors["Parámetros vs rendimiento"])
    st.subheader("🔎 Parámetros vs rendimiento")
    render_param_vs_score(trials_df)

    render_section_anchor(section_anchors["Mejores hiperparámetros"])
    st.subheader("🏆 Mejores hiperparámetros")
    render_best_params_summary(best_params_df)

    if selected_section:
        scroll_to_section(section_anchors.get(selected_section))


if __name__ == "__main__":
    st.set_page_config(
        page_title="TFG – Hiperparametrización",
        layout="wide",
    )
    processing_dir = st.session_state.processing_dir
    render_hyperparameter_analysis(processing_dir)
