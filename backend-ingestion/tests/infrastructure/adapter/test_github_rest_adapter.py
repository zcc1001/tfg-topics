from datetime import datetime
from unittest.mock import MagicMock, patch

import requests

from ingestion.domain.entities.entities import (
    IssueData,
    ReadmeData,
    TextData,
    ThesisData,
)
from ingestion.infrastructure.adapter.github_rest_adapter import GithubRestAdapter


def test_init_with_token() -> None:
    """Adapter includes Authorization header when token provided."""
    adapter = GithubRestAdapter(token="test_token")
    assert "Authorization" in adapter.headers
    assert adapter.headers["Authorization"] == "token test_token"


def test_init_without_token() -> None:
    """Adapter omits Authorization header when no token is provided."""
    adapter = GithubRestAdapter()
    assert "Authorization" not in adapter.headers


def test_handle_response_200() -> None:
    """A 200 HTTP response should return parsed JSON."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "success"}
    result = adapter._handle_response(mock_response)
    assert result == {"data": "success"}


def test_handle_response_404() -> None:
    """A 404 response should return None (not found)."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.url = "http://test.url/repo"
    result = adapter._handle_response(mock_response)
    assert result is None


def test_handle_response_403() -> None:
    """A 403 response (rate limited) should return None."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.headers = {"X-RateLimit-Remaining": "0"}
    result = adapter._handle_response(mock_response)
    assert result is None


def test_handle_response_500() -> None:
    """A 500 server error should be handled gracefully and return None."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    result = adapter._handle_response(mock_response)
    assert result is None


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_get_issues_success(mock_get: MagicMock) -> None:
    """get_issues should fetch pages and return only non-PR issues."""
    adapter = GithubRestAdapter()
    mock_response_page1 = MagicMock(spec=requests.Response)
    mock_response_page1.status_code = 200
    mock_response_page1.json.return_value = [
        {"number": 1, "title": "Issue 1", "body": "Body 1"},
        {"number": 2, "title": "Issue 2", "body": "Body 2", "pull_request": {}},
    ]
    mock_response_page2 = MagicMock(spec=requests.Response)
    mock_response_page2.status_code = 200
    mock_response_page2.json.return_value = []
    mock_get.side_effect = [mock_response_page1, mock_response_page2]

    issues = adapter.get_issues("owner", "repo")

    assert len(issues) == 1
    assert isinstance(issues[0], IssueData)
    assert issues[0].issue_id == 1
    assert issues[0].title == "Issue 1"
    assert mock_get.call_count == 2


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_get_readme_success(mock_get: MagicMock) -> None:
    """get_readme should parse download_url and content from the API."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "download_url": "http://example.com/README.md",
        "content": "bW9jayBjb250ZW50",  # "mock content" in base64
    }
    mock_get.return_value = mock_response

    readme = adapter.get_readme("owner", "repo")

    assert isinstance(readme, ReadmeData)
    assert readme.thesis_id == -1
    assert readme.download_url == "http://example.com/README.md"
    assert readme.content == "bW9jayBjb250ZW50"
    assert isinstance(readme.retrieved_at, datetime)


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_get_readme_not_found(mock_get: MagicMock) -> None:
    """Missing README (404) returns None."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.url = "http://test.url/repo"
    mock_get.return_value = mock_response

    readme = adapter.get_readme("owner", "repo")

    assert readme is None


@patch.object(GithubRestAdapter, "_get_default_branch", return_value="main")
@patch.object(
    GithubRestAdapter, "_get_repo_tree", return_value=["tex/1_Introduccion.tex"]
)
@patch.object(GithubRestAdapter, "_download_raw_file", return_value="file content")
def test_get_thesis_data_success(
    mock_download: MagicMock, mock_tree: MagicMock, mock_branch: MagicMock
) -> None:
    """get_thesis_data should build ThesisData from repo files."""
    adapter = GithubRestAdapter()
    adapter.TARGET_LATEX_FILES = ["tex/1_Introduccion.tex"]
    thesis_data = adapter.get_thesis_data("owner", "repo")

    assert isinstance(thesis_data, ThesisData)
    assert len(thesis_data.texts) == 1
    assert isinstance(thesis_data.texts[0], TextData)
    assert thesis_data.texts[0].contents == "file content"
    assert thesis_data.texts[0].section == "1_introduccion"
    mock_branch.assert_called_once_with("owner", "repo")
    mock_tree.assert_called_once_with("owner", "repo", "main")
    mock_download.assert_called_once_with(
        owner="owner", repo="repo", branch="main", path="tex/1_Introduccion.tex"
    )


def test_find_target_latex_files() -> None:
    """Find and normalize target latex file paths from a tree listing."""
    adapter = GithubRestAdapter()
    tree_paths = [
        "src/main.py",
        "docs/tex/1_Introduccion.tex",
        "README.md",
        "tex/2_Objetivos_del_proyecto.tex",
    ]
    target_suffixes = ["tex/1_Introduccion.tex", "tex/2_Objetivos_del_proyecto.tex"]

    found_files = adapter._find_target_latex_files(tree_paths, target_suffixes)

    assert len(found_files) == 2
    assert "tex/1_introduccion.tex" in found_files
    assert found_files["tex/1_introduccion.tex"] == "docs/tex/1_Introduccion.tex"
    assert "tex/2_objetivos_del_proyecto.tex" in found_files
    assert (
        found_files["tex/2_objetivos_del_proyecto.tex"]
        == "tex/2_Objetivos_del_proyecto.tex"
    )


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_get_default_branch(mock_get: MagicMock) -> None:
    """_get_default_branch should return branch name from repo metadata."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"default_branch": "develop"}
    mock_get.return_value = mock_response

    branch = adapter._get_default_branch("owner", "repo")
    assert branch == "develop"


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_get_repo_tree(mock_get: MagicMock) -> None:
    """_get_repo_tree should extract file paths from the git tree response."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "tree": [{"path": "src/main.py"}, {"path": "README.md"}]
    }
    mock_get.return_value = mock_response

    tree = adapter._get_repo_tree("owner", "repo", "main")
    assert tree == ["src/main.py", "README.md"]


@patch("ingestion.infrastructure.adapter.github_rest_adapter.requests.get")
def test_download_raw_file(mock_get: MagicMock) -> None:
    """_download_raw_file returns raw text when HTTP 200."""
    adapter = GithubRestAdapter()
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.text = "file content"
    mock_get.return_value = mock_response

    content = adapter._download_raw_file("owner", "repo", "main", "src/main.py")
    assert content == "file content"
