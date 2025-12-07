# app/domain/interfaces.py
"""
Interfaces (abstract contracts) for pluggable infrastructure.

Keep concrete implementations behind these interfaces to preserve inversion of control.
"""

from typing import List
from abc import ABC, abstractmethod
from app.domain.entities import NewsItem
from app.core.config import Settings


class NewsFetcherInterface(ABC):
    """
    Interface for a news fetcher that returns normalized NewsItem objects.
    """

    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """
        Fetch news items from configured sources and return a list of NewsItem.
        """
        raise NotImplementedError


class ClassifierInterface(ABC):
    """
    Interface for a classifier service.
    """

    @abstractmethod
    def classify(self, title: str, settings: Settings, summary: str = "") -> str:
        """
        Classify text and return a list of category labels.
        """
        raise NotImplementedError


class EmailerInterface(ABC):
    """
    Interface for an email-sending implementation.
    """

    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None:
        """
        Send a message (raises on failure).
        """
        raise NotImplementedError
