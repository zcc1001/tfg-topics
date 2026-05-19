from unittest.mock import Mock

from processing.application.ports.dataset_state_port import DatasetStatePort
from processing.application.usecases.ensure_processing_dataset_consistency import (
    EnsureProcessingDatasetConsistencyUseCase,
)


def test_ensure_processing_dataset_consistency_usecase() -> None:
    mock_port = Mock(spec=DatasetStatePort)
    mock_port.read_current_dataset_hash.return_value = "fake-hash"

    usecase = EnsureProcessingDatasetConsistencyUseCase(mock_port)
    dataset_hash = usecase.execute("fake-dataset", "fake-model")

    assert dataset_hash == "fake-hash"
    mock_port.read_current_dataset_hash.assert_called_once_with("fake-dataset")
    mock_port.invalidate_mismatched_results.assert_called_once_with(
        dataset="fake-dataset", current_hash="fake-hash"
    )
