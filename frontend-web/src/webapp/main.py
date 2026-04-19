import logging
import os
from pathlib import Path

import streamlit as st

from webapp.logging_config import configure_application_logging
from webapp.ui.components.app_footer import render_app_footer
from webapp.ui.pages.comparison_page import render_comparison
from webapp.ui.pages.document_analysis_page import render_document_analysis
from webapp.ui.pages.hyperparameter_analysis_page import render_hyperparameter_analysis
from webapp.ui.pages.model_analysis_page import render_model_analysis

logger = logging.getLogger(__name__)


def _render_model_summary_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Resumen ejecutivo",
    )


def _render_model_topics_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Exploración de tópicos",
    )


def _render_model_map_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Mapa intertópico",
    )


def _render_hyper_evolution_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Evolución del score",
    )


def _render_hyper_param_vs_score_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Parámetros vs rendimiento",
    )


def _render_hyper_best_params_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section="Mejores hiperparámetros",
    )


def _render_comparison_summary_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section="Resumen comparativo",
    )


def _render_comparison_ranking_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section="Ranking global",
    )


def _render_comparison_metrics_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section="Comparación de métricas",
    )


def _render_document_analysis_page() -> None:
    render_document_analysis(
        processing_dir=st.session_state.processing_dir,
        ingestion_dir=st.session_state.ingestion_dir,
    )


def main() -> None:
    # in/out paths from environment variables
    project_root = Path(__file__).resolve().parents[3]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    processing_dir = os.path.join(data_dir, "processing")
    ingestion_dir = os.path.join(data_dir, "ingestion")
    configure_application_logging(data_dir=data_dir, application_name="frontend")
    logger.info("Frontend started")

    if "processing_dir" not in st.session_state:
        st.session_state["processing_dir"] = processing_dir
    if "ingestion_dir" not in st.session_state:
        st.session_state["ingestion_dir"] = ingestion_dir

    st.set_page_config(page_title="TFG – Topic Modeling", layout="wide")

    logo_dir = Path(__file__).resolve().parent / "ui" / "assets"
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
                padding-top: 1rem;
            }

            section[data-testid="stSidebar"]
            [data-testid="stSidebarHeader"] img {
                height: 4.25rem !important;
                max-height: 4.25rem !important;
                width: auto !important;
                max-width: 14rem !important;
                object-fit: contain !important;
            }

            section[data-testid="stSidebar"]
            [data-testid="stSidebarHeader"] button + div img,
            section[data-testid="stSidebar"]
            [data-testid="stSidebarHeader"] div + button + div img {
                height: 4.25rem !important;
                max-height: 4.25rem !important;
            }

            [data-testid="stSidebarCollapsedControl"] + div img,
            header img[src*="tfg_topics_icon.svg"] {
                height: 2.5rem !important;
                max-height: 2.5rem !important;
                width: 2.5rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.logo(
        image=str(logo_dir / "tfg_topics_logo.svg"),
        icon_image=str(logo_dir / "tfg_topics_icon.svg"),
        size="large",
    )

    pg = st.navigation(
        {
            "Análisis por modelo": [
                st.Page(
                    _render_model_summary_page,
                    title="Resumen ejecutivo",
                    icon=":material/dashboard:",
                ),
                st.Page(
                    _render_model_topics_page,
                    title="Exploración de tópicos",
                    icon=":material/tag:",
                ),
                st.Page(
                    _render_model_map_page,
                    title="Mapa intertópico",
                    icon=":material/map:",
                ),
            ],
            "Hiperparametrización": [
                st.Page(
                    _render_hyper_evolution_page,
                    title="Evolución del score",
                    icon=":material/show_chart:",
                ),
                st.Page(
                    _render_hyper_param_vs_score_page,
                    title="Parámetros vs rendimiento",
                    icon=":material/tune:",
                ),
                st.Page(
                    _render_hyper_best_params_page,
                    title="Mejores hiperparámetros",
                    icon=":material/emoji_events:",
                ),
            ],
            "Comparativa de modelos": [
                st.Page(
                    _render_comparison_summary_page,
                    title="Resumen comparativo",
                    icon=":material/table_chart:",
                ),
                st.Page(
                    _render_comparison_ranking_page,
                    title="Ranking global",
                    icon=":material/leaderboard:",
                ),
                st.Page(
                    _render_comparison_metrics_page,
                    title="Comparación de métricas",
                    icon=":material/bar_chart:",
                ),
            ],
            "Análisis académico de documentos": [
                st.Page(
                    _render_document_analysis_page,
                    title="Análisis académico de documentos",
                    icon=":material/article:",
                ),
            ],
        },
        position="sidebar",
    )

    pg.run()
    render_app_footer()


if __name__ == "__main__":
    main()
