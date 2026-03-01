from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ingestion.domain.entities.ingestion_summary import IngestionSummary


@dataclass(frozen=True)
class ExecutionReport:
    run_id: str
    started_at: datetime
    finished_at: datetime
    status: str
    selected_targets: list[str]
    dataset_summaries: list[IngestionSummary]
    error_message: Optional[str] = None
