"""Snippet domain models."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Snippet:
    name: str
    query: str
    description: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=datetime.now)
