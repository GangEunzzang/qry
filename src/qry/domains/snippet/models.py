"""Snippet domain models."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Snippet:
    name: str
    query: str
    description: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
