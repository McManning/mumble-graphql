
import asyncio
import typing
import strawberry

from events import EventManager, text_message_events, user_change_events, channel_change_events
from schema_types import ChannelChangeEvent, TextMessageEvent, UserChangeEvent


async def create_subscription(manager: EventManager):
    try:
        subscription_id = manager.add_subscriber()

        while True:
            events = manager.flush_subscriber(subscription_id)
            if len(events) > 0:
                yield events

            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        if subscription_id:
            manager.remove_subscriber(subscription_id)
    except Exception as e:
        # Server shutdown or otherwise disconnection
        print(f"Error in subscription: {e}")
        manager.remove_subscriber(subscription_id)
        raise ValueError(f"Error in subscription: {e}")


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> typing.AsyncGenerator[int, None]:
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)

    @strawberry.subscription
    async def text_message(self) -> typing.AsyncGenerator[list[TextMessageEvent], None]:
        return create_subscription(text_message_events)

    @strawberry.subscription
    async def user_change(self) -> typing.AsyncGenerator[list[UserChangeEvent], None]:
        return create_subscription(user_change_events)

    @strawberry.subscription
    async def channel_change(self) -> typing.AsyncGenerator[list[ChannelChangeEvent], None]:
        return create_subscription(channel_change_events)
