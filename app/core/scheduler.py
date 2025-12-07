# app/core/scheduler.py
"""
Pluggable scheduler for News Alert System.
"""

from abc import ABC, abstractmethod
from typing import Callable
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)


class SchedulerInterface(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError


class BackgroundThreadScheduler(SchedulerInterface):
    """
    Thread-based scheduler using Event.wait(),
    allowing instant shutdown instead of waiting for sleep().
    """

    def __init__(self, task: Callable, interval_seconds: int = 30):
        self.task = task
        self.interval_seconds = interval_seconds
        self._thread: Thread | None = None
        self._stop_event = Event()

    def _loop(self):
        logger.info("BackgroundThreadScheduler started (interval=%s s)", self.interval_seconds)

        while not self._stop_event.wait(self.interval_seconds): 
            try:
                self.task()
            except Exception:
                logger.exception("BackgroundThreadScheduler task failed")

        logger.info("BackgroundThreadScheduler stopped")

    def start(self) -> None:
        if self._thread is not None:
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None


class NuvomScheduler(SchedulerInterface):
    """Placeholder for future Nuvom integration."""

    def start(self) -> None:
        logger.info("NuvomScheduler start called (not implemented)")

    def stop(self) -> None:
        logger.info("NuvomScheduler stop called (not implemented)")


class NoOpScheduler(SchedulerInterface):
    """Disabled scheduler mode."""

    def start(self) -> None:
        logger.info("NoOpScheduler: start called - nothing to do")

    def stop(self) -> None:
        logger.info("NoOpScheduler: stop called - nothing to do")


def create_scheduler(task: Callable, mode: str = "background", interval_seconds: int = 30) -> SchedulerInterface:
    mode = mode.lower()

    if mode == "background":
        return BackgroundThreadScheduler(task=task, interval_seconds=interval_seconds)

    if mode == "nuvom":
        return NuvomScheduler()

    return NoOpScheduler()
