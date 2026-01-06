import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import lda
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.domain_stopwords import (
    DOMAIN_STOPWORDS,
    LATEX_STOPWORDS,
)
from processing.application.services.latex_text_processor import LatexTextProcessor
from processing.domain.entities import TopicModelResult

logger = logging.getLogger(__name__)


class LdaTopicModelAdapter(TopicModelPort):

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

        SPANISH_STOPWORDS = set(stopwords.words("spanish"))
        self.STOPWORDS = (
            ENGLISH_STOP_WORDS.union(SPANISH_STOPWORDS)
            .union(DOMAIN_STOPWORDS)
            .union(LATEX_STOPWORDS)
        )

        # Cache preprocessing results (single dataset per execution)
        self._cached_tokens: Optional[List[List[str]]] = None
        self._cached_joined: Optional[List[str]] = None

    def model_name(self) -> str:
        return "lda"

    def suggest_params(self, trial: Any) -> Dict[str, Any]:
        return {
            "num_topics": trial.suggest_int("num_topics", 5, 10),
            "alpha": trial.suggest_float("alpha", 0.01, 1.0),
            "n_iter": trial.suggest_int("n_iter", 100, 300),
            "eta": trial.suggest_float("eta", 0.01, 1.0),
            "ngram_min": trial.suggest_int("ngram_min", 1, 1),
            "ngram_max": trial.suggest_int("ngram_max", 1, 2),
        }

    def _train(
        self,
        joined_texts: List[str],
        params: Dict[str, Any],
    ) -> Tuple[lda.LDA, CountVectorizer]:
        logger.info("Starting LDA model training.")
        logger.debug("Training with parameters: %s", params)

        vectorizer = CountVectorizer(
            ngram_range=(params["ngram_min"], params["ngram_max"]),
        )

        doc_term_matrix = vectorizer.fit_transform(joined_texts)
        logger.info(
            "Created document-term matrix with shape: %s", doc_term_matrix.shape
        )

        model = lda.LDA(
            n_topics=params["num_topics"],
            alpha=params["alpha"],
            n_iter=params["n_iter"],
            eta=params["eta"],
            random_state=self.random_seed,
        )

        model.fit(doc_term_matrix)
        logger.info("LDA model training completed.")

        return model, vectorizer

    def train_and_evaluate(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> float:
        logger.info("Starting model training and evaluation for %d texts.", len(texts))
        logger.debug("Using parameters: %s", params)

        tokens, joined = self._preprocess(documents=texts)

        model, vectorizer = self._train(joined_texts=joined, params=params)
        topic_word = model.topic_word_

        topics = self._extract_topics(
            topic_word, vectorizer.get_feature_names_out().tolist()
        )
        coherence = self._compute_coherence(tokens, topics)

        logger.info("Evaluation finished. Coherence score: %.4f", coherence)
        return coherence

    def fit(
        self,
        dataset: str,
        texts: List[str],
        params: Dict[str, Any],
    ) -> TopicModelResult:
        logger.info("Fitting LDA model to %d documents.", len(texts))
        logger.debug("Using parameters: %s", params)
        start_time = time.perf_counter()

        tokens, joined = self._preprocess(documents=texts)
        model, vectorizer = self._train(joined, params)
        doc_topic = model.doc_topic_  # topic distributions for document
        topic_word = model.topic_word_  # topics vectors

        topics = self._extract_topics(
            topic_word, vectorizer.get_feature_names_out().tolist()
        )
        document_topics = self._extract_document_topics(doc_topic)

        coherence = self._compute_coherence(tokens, topics)
        logger.info("Computed coherence score: %.4f", coherence)

        topic_coordinates = self._compute_intertopic_coordinates(
            topic_word=topic_word,
            doc_topic=doc_topic,
        )

        end_time = time.perf_counter()
        runtime_seconds = end_time - start_time

        result = TopicModelResult(
            dataset=dataset,
            model_name=self.model_name(),
            topics=topics,
            document_topics=document_topics,
            metrics={"coherence": coherence},
            params=params,
            topic_coordinates=topic_coordinates,
            runtime_seconds=runtime_seconds,
        )
        logger.info("LDA model fitting completed.")
        return result

    @staticmethod
    def _extract_topics(
        topic_word: np.ndarray,
        feature_names: List[str],
        top_n: int = 10,
    ) -> Dict[int, List[str]]:
        topics = {}

        for topic_idx, word_dist in enumerate(topic_word):
            top_indices = np.argsort(word_dist)[::-1][:top_n]
            topics[topic_idx] = [feature_names[i] for i in top_indices]

        return topics

    @staticmethod
    def _extract_document_topics(
        doc_topic: np.ndarray,
    ) -> List[Dict[str, Any]]:
        logger.info(
            "Extracting document-topic distributions for %d documents.", len(doc_topic)
        )
        results = []

        for doc_id, topic_dist in enumerate(doc_topic):
            for topic_id, prob in enumerate(topic_dist):
                results.append(
                    {
                        "document_id": doc_id,
                        "topic_id": topic_id,
                        "probability": float(prob),
                    }
                )

        return results

    @staticmethod
    def _compute_coherence(
        tokens: List[List[str]],
        topics: Dict[int, List[str]],
    ) -> float:
        logger.info("Computing coherence score.")
        dictionary = Dictionary(tokens)
        topic_words = list(topics.values())

        coherence_model = CoherenceModel(
            topics=topic_words,
            texts=tokens,
            dictionary=dictionary,
            coherence="c_v",
        )

        coherence = float(coherence_model.get_coherence())
        logger.info("Coherence score (c_v): %.4f", coherence)
        return coherence

    def _preprocess(
        self,
        documents: List[str],
    ) -> Tuple[List[List[str]], List[str]]:
        """
        Preprocesses raw documents and returns:
        - tokenized texts (for coherence)
        - joined texts (for CountVectorizer / LDA)
        """
        if self._cached_tokens is not None and self._cached_joined is not None:
            return self._cached_tokens, self._cached_joined

        logger.info("Preprocessing %d documents.", len(documents))
        tokens = [
            [
                token
                for token in simple_preprocess(LatexTextProcessor.clean(doc))
                if token not in self.STOPWORDS
            ]
            for doc in documents
        ]

        joined = [" ".join(doc_tokens) for doc_tokens in tokens]

        # Cache results
        self._cached_tokens = tokens
        self._cached_joined = joined

        logger.info(
            "Preprocessing complete. Returning %d tokenized and joined texts.",
            len(tokens),
        )
        return tokens, joined

    def _compute_intertopic_coordinates(
        self,
        topic_word: np.ndarray,
        doc_topic: np.ndarray,
    ) -> list[dict]:

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(topic_word)
        topic_sizes = doc_topic.sum(axis=0)

        result = []
        for topic_id in range(topic_word.shape[0]):
            result.append(
                {
                    "topic_id": topic_id,
                    "x": float(coords[topic_id, 0]),
                    "y": float(coords[topic_id, 1]),
                    "size": float(topic_sizes[topic_id]),
                }
            )

        return result
