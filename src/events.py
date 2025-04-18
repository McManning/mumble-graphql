
import asyncio
from typing import Any, Generic, AsyncGenerator, TypeVar
from uuid import UUID, uuid4

from schema_types import ChannelChangeEvent, TextMessageEvent, UserChangeEvent

TEvent = TypeVar("TEvent")


class EventManager(Generic[TEvent]):
    """Simple pub/sub for event subscriptions."""

    def __init__(self):
        self._subscribers: dict[UUID, list[TEvent]] = {}

    def add_subscriber(self) -> UUID:
        subscription_id = uuid4()

        print('Add subscription id', subscription_id)
        self._subscribers[subscription_id] = []
        return subscription_id

    def remove_subscriber(self, subscription_id: UUID):
        if subscription_id not in self._subscribers:
            raise ValueError(
                f"Subscription ID {subscription_id} no longer valid")

        print('Remove subscription id', subscription_id)
        del self._subscribers[subscription_id]

    async def update_subscriber(self, subscription_id: UUID) -> AsyncGenerator[list[TEvent], None]:
        if subscription_id not in self._subscribers:
            raise ValueError(
                f"Subscription ID {subscription_id} no longer valid")

        if self._subscribers.get(subscription_id):
            yield self._subscribers[subscription_id]
            self._subscribers[subscription_id].clear()

        await asyncio.sleep(0.5)

    def flush_subscriber(self, subscription_id: UUID) -> list[TEvent]:
        events = self._subscribers[subscription_id]
        self._subscribers[subscription_id] = []

        return events

    def publish(self, event: TEvent):
        print('Publish event', event)

        for subscriber in self._subscribers.values():
            subscriber.append(event)


text_message_events = EventManager[TextMessageEvent]()
user_change_events = EventManager[UserChangeEvent]()
channel_change_events = EventManager[ChannelChangeEvent]()
