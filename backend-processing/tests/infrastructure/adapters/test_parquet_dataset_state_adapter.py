from pathlib import Path

import pandas as pd
import pytest

from processing.infrastructure.adapters.parquet_dataset_state_adapter import (
    ParquetDatasetStateAdapter,
)


@pytest.fixture
def adapter(tmp_path: Path) -> ParquetDatasetStateAdapter:
    ingestion_dir = tmp_path / "ingestion"
    processing_dir = tmp_path / "processing"
    ingestion_dir.mkdir()
    processing_dir.mkdir()
    return ParquetDatasetStateAdapter(str(ingestion_dir), str(processing_dir))


def test_read_current_dataset_hash_file_not_found(
    adapter: ParquetDatasetStateAdapter,
) -> None:
    with pytest.raises(FileNotFoundError):
        adapter.read_current_dataset_hash("nonexistent")


def test_read_current_dataset_hash_success(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    dataset_path = tmp_path / "ingestion" / "test_dataset.parquet"
    dataset_path.write_bytes(b"test_content")
    hash_val = adapter.read_current_dataset_hash("test_dataset")
    assert isinstance(hash_val, str)
    assert len(hash_val) > 0


def test_read_last_processed_hash_no_files(
    adapter: ParquetDatasetStateAdapter,
) -> None:
    assert adapter.read_last_processed_hash("test", "model") is None


def test_read_last_processed_hash_summary_exists(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    model_dir = tmp_path / "processing" / "model"
    model_dir.mkdir()
    df = pd.DataFrame({"dataset_hash": ["hash1"], "created_at": ["2023-01-01"]})
    df.to_parquet(model_dir / "test_model_summary.parquet")

    hash_val = adapter.read_last_processed_hash("test", "model")
    assert hash_val == "hash1"


def test_read_last_processed_hash_info_exists(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    model_dir = tmp_path / "processing" / "model"
    model_dir.mkdir()
    df = pd.DataFrame({"dataset_hash": ["hash2"]})
    df.to_parquet(model_dir / "test_model_info.parquet")

    hash_val = adapter.read_last_processed_hash("test", "model")
    assert hash_val == "hash2"


def test_invalidate_model_results_not_exist(
    adapter: ParquetDatasetStateAdapter,
) -> None:
    # Should not raise exception
    adapter.invalidate_model_results("test", "nonexistent_model")


def test_invalidate_model_results_success(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    model_dir = tmp_path / "processing" / "model"
    model_dir.mkdir()
    (model_dir / "test_summary.parquet").touch()
    (model_dir / "other.parquet").touch()

    adapter.invalidate_model_results("test", "model")

    assert not (model_dir / "test_summary.parquet").exists()
    assert (model_dir / "other.parquet").exists()


def test_invalidate_mismatched_results_not_exist(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    import shutil

    shutil.rmtree(tmp_path / "processing")
    adapter.invalidate_mismatched_results("test", "hash")


def test_invalidate_mismatched_results(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    model_dir = tmp_path / "processing" / "model1"
    model_dir.mkdir()
    df = pd.DataFrame({"dataset_hash": ["old_hash"]})
    df.to_parquet(model_dir / "test_model_info.parquet")

    (model_dir / "test_data.parquet").touch()

    adapter.invalidate_mismatched_results("test", "new_hash")

    assert not (model_dir / "test_data.parquet").exists()


def test_invalidate_mismatched_results_match(
    adapter: ParquetDatasetStateAdapter, tmp_path: Path
) -> None:
    model_dir = tmp_path / "processing" / "model1"
    model_dir.mkdir()
    df = pd.DataFrame({"dataset_hash": ["current_hash"]})
    df.to_parquet(model_dir / "test_model_info.parquet")

    (model_dir / "test_data.parquet").touch()

    adapter.invalidate_mismatched_results("test", "current_hash")

    assert (model_dir / "test_data.parquet").exists()


def test_extract_hash_empty_df() -> None:
    df = pd.DataFrame()
    assert ParquetDatasetStateAdapter._extract_hash(df) is None


def test_extract_hash_no_hash_column() -> None:
    df = pd.DataFrame({"other": [1]})
    assert ParquetDatasetStateAdapter._extract_hash(df) is None
