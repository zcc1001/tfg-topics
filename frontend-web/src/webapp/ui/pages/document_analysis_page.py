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


def render_document_analysis(processing_dir: str, ingestion_dir: str) -> None:
    st.set_page_config(
        page_title="Análisis académico de documentos",
        layout="wide",
    )

    st.title("📚 Análisis académico de documentos")
    st.caption(
        "Descubre qué temas aparecen con mayor frecuencia en los TFG y "
        "cómo se relacionan con la calificación."
    )

    dataset = "thesis"

    model = st.selectbox(
        "Modelo de análisis temático",
        ["lda", "bertopic", "fastopic", "top2vec"],
    )

    tutor = st.text_input("Tutor (opcional)")
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

        st.session_state["results"] = use_case.execute(
            dataset=dataset,
            model_name=model,
            tutor=tutor,
            year=year,
            grade_range=grade_range,
        )

    if "results" not in st.session_state:
        return

    results = st.session_state["results"]
    docs = results["documents_summary"]
    dist = results["topic_distribution"]
    topics = results["topics"]

    if docs.empty:
        st.warning("No se encontraron TFG con los filtros seleccionados.")
        return

    # ------------------------------------------------------------

    st.subheader("🔢 Resumen")
    st.metric("TFG analizados", len(docs))
    st.metric("Temas detectados", dist["topic_id"].nunique())

    # ------------------------------------------------------------

    st.subheader("📊 Temas más frecuentes")

    topic_label_map = (
        topics.set_index("topic_id")["etiqueta_tópico"].to_dict()
        if not topics.empty
        else {}
    )

    chart_data = (
        dist.groupby("topic_id")["documentos"]
        .sum()
        .rename(index=lambda tid: topic_label_map.get(tid, f"Tema {tid}"))
        .sort_values(ascending=False)
    )

    st.bar_chart(chart_data)

    if not chart_data.empty:
        top_topic = chart_data.index[0]
        top_count = chart_data.iloc[0]

        st.success(
            f"El tema más frecuente es **{top_topic}**, presente en {top_count} TFG."
        )

    # ------------------------------------------------------------

    st.subheader("🏆 Temas según calificación")

    grade_focus = st.selectbox(
        "Selecciona una categoría de nota",
        sorted(docs["grade_category"].unique()),
    )

    grade_data = docs[docs["grade_category"] == grade_focus]

    if not grade_data.empty:
        grade_chart = (
            grade_data.groupby("tópico_principal")["thesis_id"]
            .count()
            .rename(index=lambda tid: topic_label_map.get(tid, f"Tema {tid}"))
            .sort_values(ascending=False)
        )

        st.bar_chart(grade_chart)

        if not grade_chart.empty:
            st.info(
                f"En la categoría {grade_focus}, el tema más frecuente es "
                f"**{grade_chart.index[0]}**."
            )
    else:
        st.info("No hay TFG en esta categoría con los filtros seleccionados.")

    # ------------------------------------------------------------
    st.subheader("🧠 Temas detectados")

    if topics.empty:
        st.info("No se dispone de descripción textual de los temas.")
    else:
        topic_counts = (
            docs.groupby("tópico_principal")["thesis_id"]
            .count()
            .sort_values(ascending=False)
        )

        topic_label_map = topics.set_index("topic_id")["etiqueta_tópico"].to_dict()

        for topic_id, count in topic_counts.items():

            label = topic_label_map.get(topic_id, f"Tema {topic_id}")

            # Tarjeta visual
            st.markdown(
                f"""
                <div style="
                    padding:15px;
                    border-radius:10px;
                    background-color:#f5f7fa;
                    margin-bottom:8px;
                    border-left:6px solid #4f8bf9;
                ">
                    <b>{label}</b><br>
                    <span style="color:gray;">{count} TFG</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            topic_docs = docs[docs["tópico_principal"] == topic_id]

            with st.expander(f"Ver TFG del tema ({len(topic_docs)} TFG)"):

                for _, row in topic_docs.iterrows():
                    st.markdown(
                        f"**{row['title']}**  \n"
                        f"Tutor: {row['tutor_group']}  \n"
                        f"Año: {row['year_group']}  \n"
                        f"Nota: {row['grade_category']}"
                    )
                    st.divider()


if __name__ == "__main__":
    render_document_analysis(
        st.session_state.processing_dir,
        st.session_state.ingestion_dir,
    )
