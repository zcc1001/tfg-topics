from abc import ABC, abstractmethod

from ingestion.domain.entities.execution_report import ExecutionReport


class ExecutionReportPort(ABC):
    @abstractmethod
    def save_execution_report(self, report: ExecutionReport) -> None:
        """Persist execution data for one ingestion run."""
        raise NotImplementedError
