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


def render_document_analysis(processing_dir: str, ingestion_dir: str) -> None:
    st.set_page_config(
        page_title="Análisis académico de documentos",
        layout="wide",
    )

    st.title("📚 Análisis académico de documentos")
    st.caption(
        "Explora líneas temáticas de los TFG y su relación con"
        "tutores y rendimiento académico."
    )

    dataset = "thesis"

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

        st.session_state["results"] = use_case.execute(
            dataset=dataset,
            model_name=model,
            tutor=tutor_input if tutor_input else None,
            year=year if year else None,
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
    st.subheader("🔢 Resumen general")

    col1, col2, col3 = st.columns(3)

    col1.metric("TFG analizados", len(docs))
    col2.metric("Temas detectados", dist["topic_id"].nunique())
    col3.metric(
        "Nota media",
        round(
            pd.to_numeric(results["documents_raw"]["grade"], errors="coerce").mean(),
            2,
        ),
    )

    # ------------------------------------------------------------

    topic_label_map = (
        topics.set_index("topic_id")["etiqueta_tópico"].to_dict()
        if not topics.empty
        else {}
    )

    # ------------------------------------------------------------

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
            f"presente en {chart_data.iloc[0]} TFG."
        )

    # ------------------------------------------------------------
    st.subheader("👨‍🏫 Ranking académico de tutores")
    docs["grade_numeric"] = pd.to_numeric(docs["grade"], errors="coerce")
    tutor_stats = (
        docs.groupby("tutor_group")
        .agg(
            tfg_dirigidos=("thesis_id", "nunique"),
            nota_media=("grade_numeric", "mean"),
            temas_distintos=("tópico_principal", "nunique"),
        )
        .sort_values("tfg_dirigidos", ascending=False)
    )

    st.dataframe(tutor_stats)
    # ------------------------------------------------------------

    st.subheader("🧠 Temas detectados")

    topic_counts = (
        docs.groupby("tópico_principal")["thesis_id"]
        .count()
        .sort_values(ascending=False)
    )

    for topic_id, count in topic_counts.items():

        label = topic_label_map.get(topic_id, f"Tema {topic_id}")

        with st.expander(f"{label} — {count} TFG"):

            topic_docs = docs[docs["tópico_principal"] == topic_id]

            for _, row in topic_docs.iterrows():
                st.markdown(
                    f"""
                    **{row['title']}**<br>
                    Tutor: {row['tutor_group']}<br>
                    Año: {row['year_group']}<br>
                    Nota: {row['grade_category']}
                    """
                )
                st.divider()

    # ------------------------------------------------------------

    st.divider()
    st.subheader("🎯 Especialización temática (Top 3 tutores)")

    top_tutors = tutor_stats.head(3).index

    for tutor in top_tutors:

        st.markdown(f"### {tutor}")

        tutor_docs = docs[docs["tutor_group"] == tutor]

        tutor_topics = (
            tutor_docs.groupby("tópico_principal")["thesis_id"]
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


if __name__ == "__main__":
    render_document_analysis(
        st.session_state.processing_dir,
        st.session_state.ingestion_dir,
    )
