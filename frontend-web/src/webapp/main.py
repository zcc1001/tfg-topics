import os
from pathlib import Path

import streamlit as st

from webapp.ui.components.app_footer import render_app_footer


def main() -> None:
    # in/out paths from environment variables
    project_root = Path(__file__).resolve().parents[3]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    processing_dir = os.path.join(data_dir, "processing")
    ingestion_dir = os.path.join(data_dir, "ingestion")

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
                    "ui/pages/subpages/model_summary_page.py",
                    title="Resumen ejecutivo",
                    icon=":material/dashboard:",
                ),
                st.Page(
                    "ui/pages/subpages/model_topics_page.py",
                    title="Exploración de tópicos",
                    icon=":material/tag:",
                ),
                st.Page(
                    "ui/pages/subpages/model_map_page.py",
                    title="Mapa intertópico",
                    icon=":material/map:",
                ),
            ],
            "Hiperparametrización": [
                st.Page(
                    "ui/pages/subpages/hyper_evolution_page.py",
                    title="Evolución del score",
                    icon=":material/show_chart:",
                ),
                st.Page(
                    "ui/pages/subpages/hyper_param_vs_score_page.py",
                    title="Parámetros vs rendimiento",
                    icon=":material/tune:",
                ),
                st.Page(
                    "ui/pages/subpages/hyper_best_params_page.py",
                    title="Mejores hiperparámetros",
                    icon=":material/emoji_events:",
                ),
            ],
            "Comparativa de modelos": [
                st.Page(
                    "ui/pages/subpages/comparison_summary_page.py",
                    title="Resumen comparativo",
                    icon=":material/table_chart:",
                ),
                st.Page(
                    "ui/pages/subpages/comparison_ranking_page.py",
                    title="Ranking global",
                    icon=":material/leaderboard:",
                ),
                st.Page(
                    "ui/pages/subpages/comparison_metrics_page.py",
                    title="Comparación de métricas",
                    icon=":material/bar_chart:",
                ),
            ],
            "Análisis académico de documentos": [
                st.Page(
                    "ui/pages/document_analysis_page.py",
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
