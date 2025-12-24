from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class IssueData:
    repo_owner: str
    repo_name: str
    issue_id: int
    title: str
    description: str
    retrieved_at: datetime


@dataclass
class ReadmeData:
    repo_owner: str
    repo_name: str
    download_url: str
    content: str
    retrieved_at: datetime


@dataclass
class TextData:
    contents: str
    section: str


@dataclass
class ThesisData:
    repo_owner: str
    repo_name: str
    texts: List[TextData]
    retrieved_at: datetime


@dataclass
class RepositoryInfo:
    name: str
    owner: str
    type: str
