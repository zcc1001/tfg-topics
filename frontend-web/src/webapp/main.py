import logging
import os
from pathlib import Path

import streamlit as st

from webapp.logging_config import configure_application_logging
from webapp.ui.components.app_footer import render_app_footer
from webapp.ui.i18n import _, language_selector
from webapp.ui.pages.comparison_page import render_comparison
from webapp.ui.pages.document_analysis_page import render_document_analysis
from webapp.ui.pages.hyperparameter_analysis_page import render_hyperparameter_analysis
from webapp.ui.pages.model_analysis_page import render_model_analysis

logger = logging.getLogger(__name__)


def _render_model_summary_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("model.summary")),
    )


def _render_model_topics_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("model.exploration")),
    )


def _render_model_map_page() -> None:
    render_model_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("model.map")),
    )


def _render_hyper_evolution_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("hyper.score_evo")),
    )


def _render_hyper_param_vs_score_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("hyper.param_vs_score")),
    )


def _render_hyper_best_params_page() -> None:
    render_hyperparameter_analysis(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("hyper.best_params")),
    )


def _render_comparison_summary_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("comparison.summary")),
    )


def _render_comparison_ranking_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("comparison.ranking")),
    )


def _render_comparison_metrics_page() -> None:
    render_comparison(
        base_dir=st.session_state.processing_dir,
        selected_section=str(_("comparison.metrics")),
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

    language_selector()

    modo_options = [_("menu.academic_mode"), _("menu.technical_mode")]
    modo_captions = [_("menu.academic_mode_help"), _("menu.technical_mode_help")]
    modo = st.sidebar.radio(
        _("menu.profile_selector"),
        modo_options,
        index=0,
        captions=modo_captions,
    )

    if modo == modo_options[0]:
        pages = {
            _("menu.group_exploration"): [
                st.Page(
                    _render_document_analysis_page,
                    title=_("pages.document_analysis"),
                    icon=":material/school:",
                    url_path="documentos",
                ),
            ],
        }
    else:
        pages = {
            _("menu.group_models"): [
                st.Page(
                    _render_model_summary_page,
                    title=_("pages.model_summary"),
                    icon=":material/dashboard:",
                    url_path="modelo-resumen",
                ),
                st.Page(
                    _render_model_topics_page,
                    title=_("pages.model_topics"),
                    icon=":material/tag:",
                    url_path="modelo-topicos",
                ),
                st.Page(
                    _render_model_map_page,
                    title=_("pages.model_map"),
                    icon=":material/map:",
                    url_path="modelo-mapa",
                ),
            ],
            _("menu.group_hyper"): [
                st.Page(
                    _render_hyper_evolution_page,
                    title=_("pages.hyper_evolution"),
                    icon=":material/show_chart:",
                    url_path="hiper-evolucion",
                ),
                st.Page(
                    _render_hyper_param_vs_score_page,
                    title=_("pages.hyper_params"),
                    icon=":material/tune:",
                    url_path="hiper-parametros",
                ),
                st.Page(
                    _render_hyper_best_params_page,
                    title=_("pages.hyper_best"),
                    icon=":material/emoji_events:",
                    url_path="hiper-mejores-parametros",
                ),
            ],
            _("menu.group_comparison"): [
                st.Page(
                    _render_comparison_summary_page,
                    title=_("pages.comp_summary"),
                    icon=":material/table_chart:",
                    url_path="comparativa-resumen",
                ),
                st.Page(
                    _render_comparison_ranking_page,
                    title=_("pages.comp_ranking"),
                    icon=":material/leaderboard:",
                    url_path="comparativa-ranking",
                ),
                st.Page(
                    _render_comparison_metrics_page,
                    title=_("pages.comp_metrics"),
                    icon=":material/bar_chart:",
                    url_path="comparativa-metricas",
                ),
            ],
        }
    wiki_url = "https://github.com/zcc1001/tfg-topics/wiki"
    st.sidebar.divider()
    st.sidebar.markdown(
        f"[{_('menu.help_link')}]({wiki_url})",
        help=_("menu.help_caption"),
    )

    pg = st.navigation(pages, position="sidebar")

    pg.run()
    render_app_footer()


if __name__ == "__main__":
    main()
