from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Topic:
    topic_id: int
    top_words: List[Tuple[str, float]]


@dataclass
class Metrics:
    coherence: float
    diversity: float
    perplexity: Optional[float]


@dataclass
class TopicModelResult:
    model_name: str
    topics: List[Topic]
    metrics: Metrics
