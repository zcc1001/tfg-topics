import pandas as pd
import streamlit as st
from wordcloud import WordCloud


def render_wordcloud(topics_df: pd.DataFrame, max_topics_to_render: int = 6) -> None:
    """
    Renders word clouds for the topics in the provided DataFrame,
    displayed in two columns.
    Args:
        topics_df: DataFrame containing the words and ranks of the topics.
                   Expected columns: 'topic_id', 'word', 'rank'.
        max_topics_to_render: The maximum number of word clouds to display.
    """
    st.subheader(f"Top {max_topics_to_render} - Word Clouds")
    st.caption(
        "Cada nube representa los términos más representativos de un tópico, "
        "ponderados por su importancia relativa dentro del modelo."
    )
    if "topic_id" not in topics_df.columns:
        st.error("The topics DataFrame must contain a 'topic_id' column.")
        return

    unique_topics = sorted(topics_df["topic_id"].unique())

    num_topics_to_render = min(len(unique_topics), max_topics_to_render)

    if num_topics_to_render == 0:
        st.warning("No topics to display.")
        return

    cols = st.columns(2)
    for i, topic_id in enumerate(unique_topics[:num_topics_to_render]):
        with cols[i % 2]:
            with st.container(border=True):
                topic_words_df = topics_df[topics_df["topic_id"] == topic_id]

                words = topic_words_df[["word", "rank"]]

                # We use 1/rank as a simple weight
                frequencies = {
                    row["word"]: 1.0 / row["rank"] for _, row in words.iterrows()
                }

                if not frequencies:
                    continue

                wc = WordCloud(
                    width=400,
                    height=200,
                    background_color="white",
                )

                try:
                    img = wc.generate_from_frequencies(frequencies)
                    st.image(
                        img.to_array(),
                        caption=f"WordCloud – Topic {topic_id}",
                        width="content",
                    )
                except ValueError:
                    st.warning(
                        f"Could not generate WordCloud for Topic {topic_id} "
                        f"(possibly no words)."
                    )
