from pathlib import Path

import pytest

from ingestion.domain.entities.entities import RepositoryInfo
from ingestion.infrastructure.adapter import repo_list_csv_reader


def test_fetch_repo_list_valid_rows(tmp_path: Path) -> None:
    """Verify CSV parsing: trimming fields and handling empty names.

    The CSV contains rows with surrounding whitespace and an empty name
    after stripping; the reader should return RepositoryInfo objects with
    trimmed values and preserve empty strings when applicable.
    """
    csv_content = """owner,name,type
    alice,proj1,public,
    bob , proj2 , private,
    charlie, ,public
    """
    path = tmp_path / "repos.csv"
    path.write_text(csv_content, encoding="utf-8")

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    repos = reader.fetch_repo_list()

    # three rows: second should be trimmed, third yields empty name after strip
    assert len(repos) == 3
    assert isinstance(repos[0], RepositoryInfo)
    assert repos[0].owner == "alice"
    assert repos[0].name == "proj1"
    assert repos[1].owner == "bob"
    assert repos[1].name == "proj2"
    assert repos[2].owner == "charlie"
    assert repos[2].name == ""


def test_fetch_repo_list_file_not_found() -> None:
    """Ensure a FileNotFoundError is raised for a missing CSV file."""
    missing = Path("nonexistent-file.csv")
    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(missing))
    with pytest.raises(FileNotFoundError) as exc:
        reader.fetch_repo_list()

    assert str(missing) in str(exc.value)


def test_fetch_repo_list_raises_runtime_on_reader_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Raise RuntimeError when the CSV DictReader raises an unexpected error."""
    path = tmp_path / "repos.csv"
    path.write_text("owner,name,type\n", encoding="utf-8")

    def bad_dict_reader(_file: object) -> None:
        raise ValueError("boom")

    monkeypatch.setattr(repo_list_csv_reader.csv, "DictReader", bad_dict_reader)

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    with pytest.raises(RuntimeError) as exc:
        reader.fetch_repo_list()

    assert "Error reading file CSV" in str(exc.value)
