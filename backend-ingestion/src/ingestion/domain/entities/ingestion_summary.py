from dataclasses import dataclass, field


@dataclass(frozen=True)
class IngestionSummary:
    data_type: str
    repos_with_data: list[str]
    repos_without_data: list[str]
    with_data_count: int
    without_data_count: int
    repo_record_counts: dict[str, int] = field(default_factory=dict)
