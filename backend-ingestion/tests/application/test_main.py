import os
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from ingestion.main import main


@pytest.fixture
def mock_env() -> Iterator[None]:
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "DATA_DIR": "/tmp/data",
            "REPOS_CSV_FILE_NAME": "test_repos.csv",
        },
    ):
        yield


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
@patch("ingestion.main.os.makedirs")
@patch("ingestion.main.RepoListCsvReaderPort")
@patch("ingestion.main.GithubRestAdapter")
@patch("ingestion.main.IngestionParquetStorage")
@patch("ingestion.main.DataIngestionUsecase")
def test_main_ingest_all(
    mock_data_ingestion_usecase: MagicMock,
    mock_ingestion_parquet_storage: MagicMock,
    mock_github_rest_adapter: MagicMock,
    mock_repo_list_csv_reader: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock,
    mock_argparse: MagicMock,
    mock_env: Iterator[None],
) -> None:
    """Test main function with 'all' ingest target."""
    mock_args = MagicMock()
    mock_args.ingest = ["all"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = True

    mock_usecase_instance = mock_data_ingestion_usecase.return_value

    main()

    mock_data_ingestion_usecase.assert_called_once_with(
        github_port=mock_github_rest_adapter.return_value,
        repo_info_reader=mock_repo_list_csv_reader.return_value,
        storage_port=mock_ingestion_parquet_storage.return_value,
    )

    mock_usecase_instance.ingest_issues_data.assert_called_once()
    mock_usecase_instance.ingest_readme_data.assert_called_once()
    mock_usecase_instance.ingest_thesis_data.assert_called_once()
    mock_usecase_instance.ingest_abstracts_data.assert_called_once()
    mock_usecase_instance.ingest_thesis_metadata.assert_called_once()


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
@patch("ingestion.main.os.makedirs")
@patch("ingestion.main.DataIngestionUsecase")
def test_main_ingest_issues(
    mock_data_ingestion_usecase: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock,
    mock_argparse: MagicMock,
    mock_env: Iterator[None],
) -> None:
    """Test main function with 'issues' ingest target."""
    mock_args = MagicMock()
    mock_args.ingest = ["issues"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = True

    mock_usecase_instance = mock_data_ingestion_usecase.return_value

    main()

    mock_usecase_instance.ingest_issues_data.assert_called_once()
    mock_usecase_instance.ingest_readme_data.assert_not_called()
    mock_usecase_instance.ingest_thesis_data.assert_not_called()
    mock_usecase_instance.ingest_thesis_metadata.assert_called_once()


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
@patch("ingestion.main.os.makedirs")
@patch("ingestion.main.DataIngestionUsecase")
def test_main_ingest_readmes(
    mock_data_ingestion_usecase: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock,
    mock_argparse: MagicMock,
    mock_env: Iterator[None],
) -> None:
    """Test main function with 'readmes' ingest target."""
    mock_args = MagicMock()
    mock_args.ingest = ["readmes"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = True

    mock_usecase_instance = mock_data_ingestion_usecase.return_value

    main()

    mock_usecase_instance.ingest_issues_data.assert_not_called()
    mock_usecase_instance.ingest_readme_data.assert_called_once()
    mock_usecase_instance.ingest_thesis_data.assert_not_called()
    mock_usecase_instance.ingest_thesis_metadata.assert_called_once()


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
@patch("ingestion.main.os.makedirs")
@patch("ingestion.main.DataIngestionUsecase")
def test_main_ingest_thesis(
    mock_data_ingestion_usecase: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock,
    mock_argparse: MagicMock,
    mock_env: Iterator[None],
) -> None:
    """Test main function with 'thesis' ingest target."""
    mock_args = MagicMock()
    mock_args.ingest = ["thesis"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = True

    mock_usecase_instance = mock_data_ingestion_usecase.return_value

    main()

    mock_usecase_instance.ingest_issues_data.assert_not_called()
    mock_usecase_instance.ingest_readme_data.assert_not_called()
    mock_usecase_instance.ingest_thesis_data.assert_called_once()
    mock_usecase_instance.ingest_thesis_metadata.assert_called_once()


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
@patch("ingestion.main.os.makedirs")
@patch("ingestion.main.DataIngestionUsecase")
def test_main_ingest_abstracts(
    mock_data_ingestion_usecase: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock,
    mock_argparse: MagicMock,
    mock_env: Iterator[None],
) -> None:
    """Test main function with 'abstracts' ingest target."""
    mock_args = MagicMock()
    mock_args.ingest = ["abstracts"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = True

    mock_usecase_instance = mock_data_ingestion_usecase.return_value

    main()

    mock_usecase_instance.ingest_issues_data.assert_not_called()
    mock_usecase_instance.ingest_readme_data.assert_not_called()
    mock_usecase_instance.ingest_thesis_data.assert_not_called()
    mock_usecase_instance.ingest_abstracts_data.assert_called_once()
    mock_usecase_instance.ingest_thesis_metadata.assert_called_once()


@patch("ingestion.main.argparse.ArgumentParser")
@patch("ingestion.main.os.path.exists")
def test_main_file_not_found(
    mock_exists: MagicMock, mock_argparse: MagicMock, mock_env: Iterator[None]
) -> None:
    """Test main function when repos.csv is not found."""
    mock_args = MagicMock()
    mock_args.ingest = ["all"]
    mock_argparse.return_value.parse_args.return_value = mock_args
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError):
        main()
