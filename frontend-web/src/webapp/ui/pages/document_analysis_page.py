import pandas as pd
import plotly.express as px
import streamlit as st

from webapp.application.usecases.analyze_documents_usecase import (
    AnalyzeDocumentsUseCase,
)
from webapp.infrastructure.adapters.metadata_parquet_repository import (
    MetadataParquetRepository,
)
from webapp.infrastructure.adapters.topic_model_parquet_repository import (
    TopicModelParquetRepository,
)
from webapp.ui.components.page_header import render_page_header
from webapp.ui.components.persistent_widgets import persistent_selectbox
from webapp.ui.components.section_scroll import render_section_anchor, scroll_to_section
from webapp.ui.i18n import _

DEFAULT_DATASETS = ["issues", "readmes", "thesis", "abstracts"]
DEFAULT_MODELS = ["lda", "bertopic", "fastopic", "top2vec"]


def render_document_analysis(
    processing_dir: str,
    ingestion_dir: str,
    selected_section: str | None = None,
) -> None:
    render_page_header(
        page_title=_("document.title"),
        description=_("document.desc"),
    )

    topic_repository = TopicModelParquetRepository(processing_dir)
    available_models = topic_repository.available_models()
    datasets = topic_repository.available_datasets()

    if not available_models or not datasets:
        st.info(_("document.no_data_files"))
        return

    datasets = datasets or DEFAULT_DATASETS
    section_key = (selected_section or "default").lower().replace(" ", "_")

    dataset = persistent_selectbox(
        label=_("common.dataset"),
        options=datasets,
        state_key="document_analysis_selected_dataset",
        widget_key=f"document_analysis_dataset_widget_{section_key}",
    )

    # ------------------------------------------------------------

    model_options = (
        topic_repository.available_models_for_dataset(dataset)
        or topic_repository.available_models()
        or DEFAULT_MODELS
    )
    model = persistent_selectbox(
        label=_("common.model"),
        options=model_options,
        state_key="document_analysis_selected_model",
        widget_key=f"document_analysis_model_widget_{section_key}",
    )

    tutor_input = st.text_input(
        _("document.filter_tutor"),
        key="document_analysis_tutor",
    )
    year = st.number_input(
        _("document.year"),
        min_value=2000,
        max_value=2030,
        step=1,
        value=None,
        key="document_analysis_year",
    )

    grade_range = st.slider(
        _("document.grade_range"),
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1,
        key="document_analysis_grade_range",
    )

    if st.button(_("common.analyze")):

        use_case = AnalyzeDocumentsUseCase(
            topic_repo=topic_repository,
            metadata_repo=MetadataParquetRepository(ingestion_dir),
        )

        try:
            st.session_state["document_analysis_results"] = use_case.execute(
                dataset=dataset,
                model_name=model,
                tutor=tutor_input if tutor_input else None,
                year=year if year else None,
                grade_range=grade_range,
            )
        except ValueError:
            st.session_state.pop("document_analysis_results", None)
            st.info(_("document.no_data_for_filters"))
            return
        st.session_state["document_analysis_dataset"] = dataset

    if "document_analysis_results" not in st.session_state:
        return

    if st.session_state.get("document_analysis_dataset") != dataset:
        st.info(_("document.press_analyze"))
        return

    results = st.session_state["document_analysis_results"]

    docs = results["documents_summary"]
    dist = results["topic_distribution"]
    topics = results["topics"]
    raw_docs = results["documents_raw"]

    if docs.empty:
        st.warning(_("document.no_docs"))
        return

    has_tutor_data = docs["tutor_group"].ne("Sin tutor").any()
    has_grade_data = docs["grade"].notna().any()
    has_year_data = docs["year_group"].ne("Sin año").any()

    section_anchors = {
        str(_("document.summary")): "document-resumen",
        str(_("document.freq_topics")): "document-temas-frecuentes",
        str(_("document.detected_topics")): "document-temas-detectados",
    }
    if has_tutor_data:
        section_anchors[str(_("document.tutor_ranking"))] = "document-ranking-tutores"
        section_anchors[str(_("document.thematic_spec"))] = "document-especializacion"

    render_section_anchor(section_anchors[str(_("document.summary"))])
    st.subheader(f"🔢 {_('document.summary')}")

    metrics = st.columns(4 if has_grade_data else 3)

    metrics[0].metric(_("document.analyzed_docs"), len(docs))
    metrics[1].metric(_("document.topics_detected"), dist["topic_id"].nunique())
    if has_year_data:
        metrics[2].metric(_("document.years_detected"), docs["year_group"].nunique())
    else:
        metrics[2].metric(_("document.thematic_groups"), dist["topic_id"].nunique())
    if has_grade_data:
        metrics[3].metric(
            _("document.avg_grade"),
            round(pd.to_numeric(raw_docs["grade"], errors="coerce").mean(), 2),
        )

    # ------------------------------------------------------------

    topic_label_map = (
        topics.set_index("topic_id")["etiqueta_tópico"].to_dict()
        if not topics.empty
        else {}
    )

    # ------------------------------------------------------------

    render_section_anchor(section_anchors[str(_("document.freq_topics"))])
    st.subheader(f"📊 {_('document.freq_topics')}")

    chart_data = (
        dist.groupby("topic_id")["documentos"]
        .sum()
        .rename(
            index=lambda tid: topic_label_map.get(
                tid, f"{_('document.theme_prefix')} {tid}"
            )
        )
        .sort_values(ascending=False)
    )

    st.bar_chart(chart_data)

    if not chart_data.empty:
        st.success(
            _("document.most_freq_topic").format(
                topic=chart_data.index[0], docs=chart_data.iloc[0]
            )
        )

    tutor_stats = pd.DataFrame()
    if has_tutor_data:
        render_section_anchor(section_anchors[str(_("document.tutor_ranking"))])
        st.subheader(f"👨‍🏫 {_('document.tutor_ranking')}")
        docs["grade_numeric"] = pd.to_numeric(docs["grade"], errors="coerce")
        tutor_stats = (
            docs[docs["tutor_group"] != "Sin tutor"]
            .groupby("tutor_group")
            .agg(
                documentos=("document_id", "nunique"),
                nota_media=("grade_numeric", "mean"),
                temas_distintos=("tópico_principal", "nunique"),
            )
            .sort_values("documentos", ascending=False)
        )

        st.dataframe(tutor_stats)

    render_section_anchor(section_anchors[str(_("document.detected_topics"))])
    st.subheader(f"🧠 {_('document.detected_topics')}")

    topic_counts = (
        docs.groupby("tópico_principal")["document_id"]
        .count()
        .sort_values(ascending=False)
    )

    for topic_id, count in topic_counts.items():

        label = topic_label_map.get(
            topic_id, f"{_('document.theme_prefix')} {topic_id}"
        )

        with st.expander(f"{label} — {count} {_('document.documents_suffix')}"):

            topic_docs = docs[docs["tópico_principal"] == topic_id]

            for idx, row in topic_docs.iterrows():
                title = row["title"] if pd.notna(row["title"]) else row["document_id"]
                st.markdown(
                    f"**{title}**  \n"
                    f"ID: {row['document_id']}  \n"
                    f"Tutor: {row['tutor_group']}  \n"
                    f"Año: {row['year_group']}  \n"
                    f"Nota: {row['grade_category']}"
                )
                st.divider()

    if has_tutor_data and not tutor_stats.empty:
        render_section_anchor(section_anchors[str(_("document.thematic_spec"))])
        st.divider()
        st.subheader(f"🎯 {_('document.spec_top3')}")

        top_tutors = tutor_stats.head(3).index

        for tutor in top_tutors:

            st.markdown(f"### {tutor}")

            tutor_docs = docs[docs["tutor_group"] == tutor]

            tutor_topics = (
                tutor_docs.groupby("tópico_principal")["document_id"]
                .count()
                .rename(
                    index=lambda tid: topic_label_map.get(
                        tid,
                        f"{_('document.theme_prefix')} {tid}",
                    )
                )
                .sort_values(ascending=True)
            )

            if not tutor_topics.empty:

                chart_df = tutor_topics.reset_index().rename(
                    columns={
                        "tópico_principal": "Tema",
                        "document_id": "Documentos",
                    }
                )

                fig = px.bar(
                    chart_df,
                    x="Documentos",
                    y="Tema",
                    orientation="h",
                    title=f"Especialización temática de {tutor}",
                    text="Documentos",
                )

                fig.update_layout(
                    height=max(350, len(chart_df) * 40),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=50, b=20),
                )

                fig.update_traces(textposition="outside")

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"tutor_chart_{tutor}",
                )

                dominant = tutor_topics.idxmax()

                st.info(_("document.dominant_line").format(dominant=dominant))

            st.divider()
    if selected_section:
        scroll_to_section(section_anchors.get(selected_section))


if __name__ == "__main__":
    st.set_page_config(
        page_title="Análisis académico de documentos",
        layout="wide",
    )
    render_document_analysis(
        st.session_state.processing_dir,
        st.session_state.ingestion_dir,
    )
