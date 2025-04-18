
import strawberry
from strawberry import ID
from mumble import get_mumble_server

from schema_types import *


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Update the welcome message for a server.")
    def update_welcome_message(self, server_id: ID, text: str) -> bool:
        server = get_mumble_server(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found")

        server.setConf("welcometext", text)
        return True

    @strawberry.mutation(description="Send text message to a single user.")
    def send_message(self, server_id: ID, session_id: ID, text: str) -> bool:
        server = get_mumble_server(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found")

        server.sendMessage(int(session_id), text)
        return True

    @strawberry.mutation(description="Send text message to channel or a tree of channels.")
    def send_channel_message(self, server_id: ID, channel_id: ID, text: str,  tree: bool = True) -> bool:
        server = get_mumble_server(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found")

        server.sendMessageChannel(int(channel_id), tree, text)
        return True

    @strawberry.mutation(description="Set user state. You can use this to move, mute and deafen users.")
    def user_state(self, server_id: ID, input: UserStateInput) -> bool:
        server = get_mumble_server(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found")

        user = server.getState(int(input.id))
        if input.mute is not None:
            user.mute = input.mute

        if input.deaf is not None:
            user.deaf = input.deaf

        if input.suppress is not None:
            user.suppress = input.suppress

        if input.channel is not None:
            user.channel = int(input.channel)

        server.setState(user)
        return True
