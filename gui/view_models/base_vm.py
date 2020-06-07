# coding: utf-8

from typing import List, TypeVar, Callable

from dataclasses import dataclass

from gui.view_models.event import Event

T = TypeVar("T", bound="BaseViewModel")
UpdateHandler = Callable[[T, Event], None]


def notifying(event: Event) -> Callable:
    def notify(f: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> None:
            f(*args, **kwargs)
            instance, *_ = args
            instance.handle(event)

        return wrapper

    return notify


@dataclass(frozen=True)
class BaseViewModel:
    _subscriptions: List[UpdateHandler]

    def subscribe(self, handler: UpdateHandler) -> None:
        self._subscriptions.append(handler)

    def unsubscribe(self, handler: UpdateHandler) -> None:
        self._subscriptions.remove(handler)

    def notify_all(self, event: Event) -> None:
        for subscription in self._subscriptions:
            subscription(self, event)

    def handle(self, event: Event) -> None:
        self.notify_all(event=event)

    def clear_subscriptions(self) -> None:
        self._subscriptions.clear()
