# app/core/scheduler.py
"""
Pluggable scheduler for News Alert System.

Provides an interface and concrete implementations for running periodic tasks:
- BackgroundThreadScheduler: simple daemon thread (demo-friendly)
- NuvomScheduler: placeholder for future Nuvom integration
- NoOpScheduler: disables scheduling (manual mode)
"""

from abc import ABC, abstractmethod
from typing import Callable
from threading import Thread
import time
import logging

logger = logging.getLogger(__name__)


class SchedulerInterface(ABC):
    """
    Abstract interface for scheduler implementations.
    """

    @abstractmethod
    def start(self) -> None:
        """
        Start the scheduler.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        raise NotImplementedError


class BackgroundThreadScheduler(SchedulerInterface):
    """
    Simple scheduler using a daemon thread that calls a task periodically.
    """

    def __init__(self, task: Callable, interval_seconds: int = 30):
        self.task = task
        self.interval_seconds = interval_seconds
        self._thread: Thread | None = None
        self._running = False

    def _loop(self):
        logger.info("BackgroundThreadScheduler started (interval=%s s)", self.interval_seconds)
        while self._running:
            try:
                self.task()
            except Exception:
                logger.exception("BackgroundThreadScheduler task failed")
            time.sleep(self.interval_seconds)
        logger.info("BackgroundThreadScheduler stopped")

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None


class NuvomScheduler(SchedulerInterface):
    """
    Placeholder for Nuvom integration.

    To implement:
    - initialize Nuvom client
    - register periodic jobs
    - start Nuvom loop
    """

    def start(self) -> None:
        logger.info("NuvomScheduler start called (not yet implemented)")

    def stop(self) -> None:
        logger.info("NuvomScheduler stop called (not yet implemented)")


class NoOpScheduler(SchedulerInterface):
    """
    No-op scheduler (manual trigger mode)
    """

    def start(self) -> None:
        logger.info("NoOpScheduler: start called - doing nothing")

    def stop(self) -> None:
        logger.info("NoOpScheduler: stop called - doing nothing")


def create_scheduler(task: Callable, mode: str = "background", interval_seconds: int = 30) -> SchedulerInterface:
    """
    Factory method to create scheduler based on mode.
    """
    mode = mode.lower()
    if mode == "background":
        return BackgroundThreadScheduler(task=task, interval_seconds=interval_seconds)
    elif mode == "nuvom":
        return NuvomScheduler()
    else:
        return NoOpScheduler()
