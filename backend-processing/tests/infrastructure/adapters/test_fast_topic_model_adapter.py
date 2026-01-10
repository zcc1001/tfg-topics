from __future__ import annotations

import sys
import types
from typing import Any, List, Tuple

import numpy as np
import pytest

if "fastopic" not in sys.modules:
    mod_fast = types.ModuleType("fastopic")

    class _DummyFASTopic:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            # will be configured by tests via attributes
            self.top_words: List[str] = []
            self.topic_embeddings = np.array([])
            self.theta = np.zeros((0, 0))

        def fit_transform(
            self, texts: Any, epochs: Any = None, learning_rate: Any = None
        ) -> Tuple[List[str], np.ndarray]:
            # return (top_words, theta)
            top_words = getattr(self, "top_words", [])
            theta = getattr(self, "theta", np.zeros((len(texts), len(top_words))))
            return top_words, theta

    mod_fast.FASTopic = _DummyFASTopic  # type: ignore
    sys.modules["fastopic"] = mod_fast

import processing.infrastructure.adapters.modeling.fastopic_model_adapter as mod
from processing.infrastructure.adapters.modeling.fastopic_model_adapter import (
    FastTopicModelAdapter,
)


class _FakeModel:
    def __init__(self, top_words: list[str], embeddings: Any) -> None:
        self.top_words = top_words
        self.topic_embeddings = embeddings


def test_extract_topics_parses_top_words() -> None:
    """_extract_topics splits top_words and ignores entries with <2 words."""

    class T(FastTopicModelAdapter):
        pass

    model = _FakeModel(
        top_words=["a b c", "singleword", "d e"], embeddings=np.array([])
    )
    topics = T._extract_topics(model)  # type: ignore

    assert 0 in topics
    assert 1 not in topics
    assert topics[0] == ["a", "b", "c"]
    assert 2 in topics and topics[2] == ["d", "e"]


def test_extract_document_topics_builds_entries() -> None:
    """_extract_document_topics returns per-document/per-topic probability entries."""
    theta = np.array([[0.1, 0.9], [0.5, 0.5]])

    class T(FastTopicModelAdapter):
        pass

    results = T._extract_document_topics(theta)
    # two docs x two topics => 4 entries
    assert len(results) == 4
    assert any(r["document_id"] == 0 and r["topic_id"] == 1 for r in results)


def test_compute_coherence_penalty_and_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    _compute_coherence returns -1.0 when no topics, otherwise delegates to
    CoherenceModel.
    """
    tokens = [["a", "b"], ["b", "c"]]

    class T(FastTopicModelAdapter):
        pass

    # No topics -> penalty
    assert T._compute_coherence(tokens, {}) == -1.0

    # Mock CoherenceModel to return a fixed score
    class DummyCoherence:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def get_coherence(self) -> float:
            return 0.123

    monkeypatch.setattr(mod, "CoherenceModel", DummyCoherence)

    topics = {0: ["a", "b"], 1: ["b", "c"]}
    score = T._compute_coherence(tokens, topics)
    assert pytest.approx(score, rel=1e-6) == 0.123


def test_preprocess_caches_and_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    """_preprocess removes STOPWORDS and caches the tokenization result."""
    # Ensure stopwords.words doesn't try to access NLTK data
    monkeypatch.setattr(mod.stopwords, "words", lambda _lang: set())

    class T(FastTopicModelAdapter):
        pass

    adapter = T(random_seed=0)
    docs = ["This is a test of stopwords filtering".lower()]

    toks1 = adapter._preprocess(docs)
    toks2 = adapter._preprocess(docs)

    assert toks1 is toks2
    assert all(isinstance(t, list) for t in toks1)
