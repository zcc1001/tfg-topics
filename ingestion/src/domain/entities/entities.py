from dataclasses import dataclass


@dataclass
class IssueData:
    number: int
    title: str
    description: str


@dataclass
class ReadmeData:
    download_url: str
    content: str


@dataclass
class RepositoryInfo:
    name: str
    owner: str
    type: str
