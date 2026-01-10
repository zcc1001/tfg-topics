from __future__ import annotations

import sys
import types
from typing import Any, List, Tuple

import numpy as np
import pytest

if "top2vec" not in sys.modules:
    mod_t2v = types.ModuleType("top2vec")

    class _DummyTop2Vec:
        def __init__(
            self,
            documents: Any = None,
            embedding_model: Any = None,
            min_count: Any = None,
            speed: Any = None,
            workers: Any = None,
            verbose: Any = None,
        ) -> None:
            # placeholders
            self.document_vectors = np.zeros((0, 0))
            self.topic_vectors = np.zeros((0, 0))

        def get_topics(self) -> Tuple[List[Any], Any, List[Any]]:
            # return topic_words, something, topic_nums
            return [], None, []

        def get_documents_topics(
            self, doc_ids: Any = None
        ) -> Tuple[List[Any], List[Any], Any, List[Any]]:
            return [], [], None, []

    mod_t2v.Top2Vec = _DummyTop2Vec  # type: ignore
    sys.modules["top2vec"] = mod_t2v

import processing.infrastructure.adapters.modeling.top2vec_topic_adapter as mod
from processing.infrastructure.adapters.modeling.top2vec_topic_adapter import (
    Top2VecModelAdapter,
)


class _FakeTop2VecModel:
    def __init__(self) -> None:
        # two documents, vectors shape (2,3)
        self.document_vectors = np.zeros((2, 3))
        # topic_vectors: 2 topics x 3 features
        self.topic_vectors = np.array([[0.1, 0.2, 0.3], [0.0, 0.5, -0.1]])

        # topics representation: list of arrays/lists
        self._topic_words = [["a", "b"], ["c", "d"]]
        self._topic_nums = [np.int64(0), np.int64(1)]

        # documents -> topics and scores
        self._doc_topics = [[0, 1], [1, 0]]
        self._doc_scores = [[0.2, 0.8], [0.5, 0.5]]

    def get_topics(self) -> Tuple[List[Any], Any, List[Any]]:
        return self._topic_words, None, self._topic_nums

    def get_documents_topics(
        self, doc_ids: Any = None
    ) -> Tuple[List[Any], List[Any], Any, List[Any]]:
        # return doc_topics, doc_scores, _, doc_ids as arrays of shape (N,)
        doc_ids_out = [np.array([i]) for i in range(self.document_vectors.shape[0])]
        return self._doc_topics, self._doc_scores, None, doc_ids_out


def test_extract_topics_returns_mapping() -> None:
    """_extract_topics converts Top2Vec get_topics output into id->words mapping."""
    model = _FakeTop2VecModel()

    class T(Top2VecModelAdapter):
        pass

    topics = T._extract_topics(model, top_n=2)  # type: ignore
    assert 0 in topics and 1 in topics
    assert topics[0] == ["a", "b"]


def test_extract_document_topics_normalizes_scores() -> None:
    """
    _extract_document_topics normalizes topic scores per document.
    """
    model = _FakeTop2VecModel()

    class T(Top2VecModelAdapter):
        pass

    results = T._extract_document_topics(model)  # type: ignore
    # two docs, first doc should have two entries
    assert any(r["document_id"] == 0 for r in results)
    assert any(r["document_id"] == 1 for r in results)
    # probabilities should sum to ~1 per document
    probs_doc0 = [r["probability"] for r in results if r["document_id"] == 0]
    assert pytest.approx(sum(probs_doc0), rel=1e-6) == 1.0


def test_compute_coherence_penalty_and_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    _compute_coherence returns -1.0 for no valid topics and delegates to
    CoherenceModel.
    """
    tokens = [["a", "b"], ["b", "c"]]

    # empty topics -> penalized
    assert Top2VecModelAdapter._compute_coherence(tokens, {}) == -1.0

    # Mock CoherenceModel
    class DummyCoherence:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def get_coherence(self) -> float:
            return 0.33

    monkeypatch.setattr(mod, "CoherenceModel", DummyCoherence)

    topics = {0: ["a", "b"], 1: ["b", "c"]}
    score = Top2VecModelAdapter._compute_coherence(tokens, topics)
    assert pytest.approx(score, rel=1e-6) == 0.33


def test_preprocess_caches_and_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    """_preprocess tokenizes, filters STOPWORDS and caches results."""
    monkeypatch.setattr(mod.stopwords, "words", lambda _lang: set())

    class T(Top2VecModelAdapter):
        pass

    adapter = T(random_seed=0)
    docs = ["This is sample text.".lower()]
    tok1 = adapter._preprocess(docs)
    tok2 = adapter._preprocess(docs)
    assert tok1 is tok2
    assert all(isinstance(t, list) for t in tok1)


def test_compute_intertopic_coordinates_various_cases() -> None:
    """
    _compute_intertopic_coordinates returns empty for invalid vectors
    and computes coords for valid ones.
    """

    class T(Top2VecModelAdapter):
        pass

    # model lacking topic_vectors -> []
    m0 = types.SimpleNamespace()
    assert T._compute_intertopic_coordinates(m0) == []  # type: ignore

    # invalid vectors shape
    m1 = types.SimpleNamespace(topic_vectors=np.array([1, 2, 3]))
    assert T._compute_intertopic_coordinates(m1) == []  # type: ignore

    # valid vectors
    vectors = np.array([[0.1, 0.2], [0.0, 0.5], [0.2, -0.2]])
    m2 = types.SimpleNamespace(topic_vectors=vectors)
    coords = T._compute_intertopic_coordinates(m2)  # type: ignore
    assert len(coords) == 3
    assert all("topic_id" in c and "x" in c and "y" in c for c in coords)
