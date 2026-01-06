import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from top2vec import Top2Vec

from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.domain_stopwords import LATEX_STOPWORDS
from processing.application.services.latex_text_processor import LatexTextProcessor
from processing.domain.entities import TopicModelResult

logger = logging.getLogger(__name__)


class Top2VecModelAdapter(TopicModelPort):

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

        SPANISH_STOPWORDS = set(stopwords.words("spanish"))
        self.STOPWORDS = ENGLISH_STOP_WORDS.union(SPANISH_STOPWORDS).union(
            LATEX_STOPWORDS
        )

        self._cached_tokens: Optional[List[List[str]]] = None

    def model_name(self) -> str:
        return "top2vec"

    def suggest_params(self, trial: Any) -> Dict[str, Any]:
        return {
            "min_count": trial.suggest_int("min_count", 1, 5),
            "speed": trial.suggest_categorical("speed", ["deep-learn"]),
            "workers": trial.suggest_int("workers", 1, 8),
        }

    def _train(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> Optional[Top2Vec]:
        try:
            model = Top2Vec(
                documents=texts,
                embedding_model="all-MiniLM-L6-v2",
                min_count=params["min_count"],
                speed=params["speed"],
                workers=params["workers"],
                verbose=False,
                hdbscan_args={
                    "min_cluster_size": 5,
                    "min_samples": 1,
                    "cluster_selection_method": "leaf",
                },
            )
        except ValueError as e:
            if "need at least one array to concatenate" in str(e):
                logger.warning(
                    "Top2Vec did not find any valid clusters "
                    "(all documents labeled as noise)."
                )
                return None
            raise
        logger.info("Top2Vec model training completed.")
        return model

    def train_and_evaluate(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> float:

        clean_texts = [LatexTextProcessor.clean(doc) for doc in texts]

        non_empty_texts = [text for text in clean_texts if text and not text.isspace()]
        if not non_empty_texts:
            logger.warning("Too few documents for Top2Vec: %d", len(non_empty_texts))
            return -1.0

        self._cached_tokens = None
        tokens = self._preprocess(non_empty_texts)

        model = self._train(non_empty_texts, params)

        if model is None:
            return -1.0

        topics = self._extract_topics(model)

        coherence = self._compute_coherence(tokens, topics)
        logger.info("Evaluation finished. Coherence score: %.4f", coherence)

        return coherence

    def fit(
        self,
        dataset: str,
        texts: List[str],
        params: Dict[str, Any],
    ) -> TopicModelResult:

        logger.info("Fitting Top2Vec model to %d documents.", len(texts))
        start_time = time.perf_counter()
        clean_texts = [LatexTextProcessor.clean(doc) for doc in texts]

        original_indices = [
            i for i, text in enumerate(clean_texts) if text and not text.isspace()
        ]
        non_empty_texts = [clean_texts[i] for i in original_indices]

        if not non_empty_texts:
            logger.warning("No documents to train on after cleaning.")
            raise RuntimeError("No documents to train on after cleaning.")

        self._cached_tokens = None
        tokens = self._preprocess(non_empty_texts)

        model = self._train(non_empty_texts, params)
        if model is None:
            raise RuntimeError(
                "Top2Vec could not find any valid topics for the "
                "given documents and parameters."
            )
        topics = self._extract_topics(model)
        document_topics_filtered = self._extract_document_topics(model)

        document_topics = []
        for doc_topic in document_topics_filtered:
            model_doc_id = doc_topic["document_id"]
            if model_doc_id < len(original_indices):
                original_doc_id = original_indices[model_doc_id]
                document_topics.append({**doc_topic, "document_id": original_doc_id})

        coherence = self._compute_coherence(tokens, topics)
        logger.info("Computed coherence score: %.4f", coherence)

        topic_coordinates = self._compute_intertopic_coordinates(model)

        end_time = time.perf_counter()
        runtime_seconds = end_time - start_time

        return TopicModelResult(
            dataset=dataset,
            model_name=self.model_name(),
            topics=topics,
            document_topics=document_topics,
            metrics={"coherence": coherence},
            params=params,
            topic_coordinates=topic_coordinates,
            runtime_seconds=runtime_seconds,
        )

    @staticmethod
    def _extract_topics(
        model: Top2Vec,
        top_n: int = 10,
    ) -> Dict[int, List[str]]:

        topic_words, _, topic_nums = model.get_topics()

        topics: Dict[int, List[str]] = {}
        for idx, words in zip(topic_nums, topic_words):
            if isinstance(idx, (int, np.integer)):
                topics[int(idx)] = list(words[:top_n])

        return topics

    @staticmethod
    def _extract_document_topics(
        model: Top2Vec,
    ) -> List[Dict[str, Any]]:

        doc_topics, doc_scores, _, doc_ids = model.get_documents_topics(
            doc_ids=list(range(model.document_vectors.shape[0]))
        )

        results: List[Dict[str, Any]] = []
        for i in range(len(doc_topics)):
            topics = doc_topics[i]
            scores = doc_scores[i]
            doc_id = doc_ids[i]

            if isinstance(doc_id, (np.ndarray, list)):
                doc_id = int(doc_id[0])
            else:
                doc_id = int(doc_id)

            if not isinstance(topics, (list, np.ndarray)):
                topics = [topics]
            if not isinstance(scores, (list, np.ndarray)):
                scores = [scores]

            score_sum = float(np.sum(scores)) if np.sum(scores) > 0 else 1.0
            for topic_id, score in zip(topics, scores):
                results.append(
                    {
                        "document_id": doc_id,
                        "topic_id": int(topic_id),
                        "probability": float(score / score_sum),
                    }
                )

        return results

    @staticmethod
    def _compute_coherence(
        tokens: List[List[str]],
        topics: Dict[int, List[str]],
    ) -> float:

        if not topics:
            return -1.0

        dictionary = Dictionary(tokens)

        filtered_topics: List[List[str]] = []
        for words in topics.values():
            valid = [w for w in words if w in dictionary.token2id]
            if len(valid) >= 2:
                filtered_topics.append(valid)

        if not filtered_topics:
            return -1.0

        coherence_model = CoherenceModel(
            topics=filtered_topics,
            texts=tokens,
            dictionary=dictionary,
            coherence="c_v",
        )

        return float(coherence_model.get_coherence())

    def _preprocess(
        self,
        documents: List[str],
    ) -> List[List[str]]:

        if self._cached_tokens is not None:
            return self._cached_tokens

        tokens = [
            [t for t in simple_preprocess(doc) if t not in self.STOPWORDS]
            for doc in documents
        ]

        self._cached_tokens = tokens
        return tokens

    @staticmethod
    def _compute_intertopic_coordinates(
        model: Top2Vec,
    ) -> List[Dict[str, Any]]:

        if not hasattr(model, "topic_vectors"):
            return []

        vectors = model.topic_vectors
        if not isinstance(vectors, np.ndarray) or vectors.ndim != 2:
            return []

        if vectors.shape[0] < 2:
            return []

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(vectors)

        result: List[Dict[str, Any]] = []
        for idx, (x, y) in enumerate(coords):
            result.append(
                {
                    "topic_id": int(idx),
                    "x": float(x),
                    "y": float(y),
                    "size": 1.0,
                }
            )

        return result
