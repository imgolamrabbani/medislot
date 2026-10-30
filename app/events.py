"""Observer pattern: modules react to domain events without knowing each other."""
from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[dict], None]) -> None:
        self._subscribers[event].append(handler)

    def publish(self, event: str, payload: dict) -> None:
        for handler in self._subscribers[event]:
            handler(payload)
