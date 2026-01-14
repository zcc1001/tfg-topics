import pandas as pd
import streamlit as st

from webapp.application.usecases.load_model_results_usecase import (
    LoadModelResultsUseCase,
)
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.best_params_summary import render_best_params_summary
from webapp.ui.components.doc_topic_distribution import render_doc_topic_distribution
from webapp.ui.components.param_vs_score import render_param_vs_score
from webapp.ui.components.render_intertopic_distance_map import (
    render_intertopic_distance_map,
)
from webapp.ui.components.render_topic_summary_table import render_topic_summary_table
from webapp.ui.components.trial_score_evolution import render_trial_score_evolution
from webapp.ui.components.wordcloud import render_wordcloud


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
            ["issues", "readmes", "thesis"],
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
        render_wordcloud(data["topics"], max_topics_to_render=6)

        render_topic_summary_table(
            data["topics"],
            max_words=10,
        )
        render_doc_topic_distribution(data["document_topics"])
        render_intertopic_distance_map(data["topic_coordinates"])
        st.divider()
        _render_hyperparameter_section(
            trials_df=data["trials"],
            best_params_df=data["best_params"],
        )


def _render_hyperparameter_section(
    trials_df: pd.DataFrame,
    best_params_df: pd.DataFrame,
) -> None:
    st.title("Hiperparametrización del modelo")
    st.caption(
        "Análisis del proceso de búsqueda de hiperparámetros "
        "y su impacto en la calidad del modelo."
    )
    render_trial_score_evolution(trials_df)
    render_param_vs_score(trials_df)
    render_best_params_summary(best_params_df)


if __name__ == "__main__":
    processing_dir = st.session_state.processing_dir
    render_model_analysis(processing_dir)
