from datetime import datetime
from dataclasses import dataclass


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
class RepositoryInfo:
    name: str
    owner: str
    type: str
