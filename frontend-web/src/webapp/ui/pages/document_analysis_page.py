import matplotlib.pyplot as plt
import pandas as pd
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
from webapp.ui.components.section_scroll import render_section_anchor, scroll_to_section


def render_document_analysis(
    processing_dir: str,
    ingestion_dir: str,
    selected_section: str | None = None,
) -> None:
    render_page_header(
        page_title="Análisis académico de documentos",
        description=(
            "Explora líneas temáticas de los distintos datasets y su relación con "
            "los metadatos disponibles."
        ),
    )

    dataset = st.selectbox(
        "Dataset",
        ["issues", "readmes", "thesis", "abstracts"],
        index=2,
    )

    # ------------------------------------------------------------

    model = st.selectbox(
        "Modelo de análisis temático",
        ["lda", "bertopic", "fastopic", "top2vec"],
    )

    tutor_input = st.text_input("Filtrar por tutor (opcional)")
    year = st.number_input(
        "Año de presentación",
        min_value=2000,
        max_value=2030,
        step=1,
        value=None,
    )

    grade_range = st.slider(
        "Rango de nota",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1,
    )

    if st.button("Analizar"):

        use_case = AnalyzeDocumentsUseCase(
            topic_repo=TopicModelParquetRepository(processing_dir),
            metadata_repo=MetadataParquetRepository(ingestion_dir),
        )

        st.session_state["document_analysis_results"] = use_case.execute(
            dataset=dataset,
            model_name=model,
            tutor=tutor_input if tutor_input else None,
            year=year if year else None,
            grade_range=grade_range,
        )
        st.session_state["document_analysis_dataset"] = dataset

    if "document_analysis_results" not in st.session_state:
        return

    if st.session_state.get("document_analysis_dataset") != dataset:
        st.info("Pulsa `Analizar` para cargar resultados del dataset seleccionado.")
        return

    results = st.session_state["document_analysis_results"]

    docs = results["documents_summary"]
    dist = results["topic_distribution"]
    topics = results["topics"]
    raw_docs = results["documents_raw"]

    if docs.empty:
        st.warning("No se encontraron documentos con los filtros seleccionados.")
        return

    has_tutor_data = docs["tutor_group"].ne("Sin tutor").any()
    has_grade_data = docs["grade"].notna().any()
    has_year_data = docs["year_group"].ne("Sin año").any()

    section_anchors = {
        "Resumen general": "document-resumen",
        "Temas más frecuentes": "document-temas-frecuentes",
        "Temas detectados": "document-temas-detectados",
    }
    if has_tutor_data:
        section_anchors["Ranking académico de tutores"] = "document-ranking-tutores"
        section_anchors["Especialización temática"] = "document-especializacion"

    render_section_anchor(section_anchors["Resumen general"])
    st.subheader("🔢 Resumen general")

    metrics = st.columns(4 if has_grade_data else 3)

    metrics[0].metric("Documentos analizados", len(docs))
    metrics[1].metric("Temas detectados", dist["topic_id"].nunique())
    if has_year_data:
        metrics[2].metric("Años detectados", docs["year_group"].nunique())
    else:
        metrics[2].metric("Grupos temáticos", dist["topic_id"].nunique())
    if has_grade_data:
        metrics[3].metric(
            "Nota media",
            round(pd.to_numeric(raw_docs["grade"], errors="coerce").mean(), 2),
        )

    # ------------------------------------------------------------

    topic_label_map = (
        topics.set_index("topic_id")["etiqueta_tópico"].to_dict()
        if not topics.empty
        else {}
    )

    # ------------------------------------------------------------

    render_section_anchor(section_anchors["Temas más frecuentes"])
    st.subheader("📊 Temas más frecuentes")

    chart_data = (
        dist.groupby("topic_id")["documentos"]
        .sum()
        .rename(index=lambda tid: topic_label_map.get(tid, f"Tema {tid}"))
        .sort_values(ascending=False)
    )

    st.bar_chart(chart_data)

    if not chart_data.empty:
        st.success(
            f"El tema más frecuente es **{chart_data.index[0]}**, "
            f"presente en {chart_data.iloc[0]} documentos."
        )

    tutor_stats = pd.DataFrame()
    if has_tutor_data:
        render_section_anchor(section_anchors["Ranking académico de tutores"])
        st.subheader("👨‍🏫 Ranking académico de tutores")
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

    render_section_anchor(section_anchors["Temas detectados"])
    st.subheader("🧠 Temas detectados")

    topic_counts = (
        docs.groupby("tópico_principal")["document_id"]
        .count()
        .sort_values(ascending=False)
    )

    for topic_id, count in topic_counts.items():

        label = topic_label_map.get(topic_id, f"Tema {topic_id}")

        with st.expander(f"{label} — {count} documentos"):

            topic_docs = docs[docs["tópico_principal"] == topic_id]

            for _, row in topic_docs.iterrows():
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
        render_section_anchor(section_anchors["Especialización temática"])
        st.divider()
        st.subheader("🎯 Especialización temática (Top 3 tutores)")

        top_tutors = tutor_stats.head(3).index

        for tutor in top_tutors:

            st.markdown(f"### {tutor}")

            tutor_docs = docs[docs["tutor_group"] == tutor]

            tutor_topics = (
                tutor_docs.groupby("tópico_principal")["document_id"]
                .count()
                .rename(index=lambda tid: topic_label_map.get(tid, f"Tema {tid}"))
                .sort_values(ascending=True)
            )

            fig, ax = plt.subplots()
            tutor_topics.plot(kind="barh", ax=ax)
            st.pyplot(fig)

            if not tutor_topics.empty:
                dominant = tutor_topics.idxmax()
                st.info(f"Línea dominante: **{dominant}**")

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
