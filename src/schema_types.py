from enum import Enum
from typing import Optional
import strawberry

import MumbleServer
from textures import get_texture_cache, set_texture_cache
from utils import address_tuple_to_ipv6


@strawberry.type
class Server:
    _server: strawberry.Private[MumbleServer.ServerPrx]

    def __init__(self, server: MumbleServer.ServerPrx):
        self._server = server

    @strawberry.field(description="Get the ID of the server.")
    def id(self) -> strawberry.ID:
        return self._server.id()

    @strawberry.field(description="Check if the server is running.")
    def is_running(self) -> bool:
        return self._server.isRunning()

    @strawberry.field(description="Get the channels for this server. This includes all nested channels as a flat list.")
    def channels(self) -> list["Channel"]:
        return [Channel(c) for c in self._server.getChannels().values()]

    @strawberry.field(description="Get all currently connected users on the server.")
    def users(self) -> list["User"]:
        return [User(u, self._server) for u in self._server.getUsers().values()]

    @strawberry.field(description="Get the welcome message for the server.")
    def welcome_message(self) -> str:
        return self._server.getConf("welcometext")


@strawberry.type
class Channel:
    _channel: strawberry.Private[MumbleServer.Channel]

    def __init__(self, channel: MumbleServer.Channel):
        self._channel = channel

    @strawberry.field(description="Get the ID of the channel.")
    def id(self) -> strawberry.ID:
        return self._channel.id

    @strawberry.field(description="Get the name of the channel.")
    def name(self) -> str:
        return self._channel.name

    @strawberry.field(description="Get the ID of the parent channel.")
    def parent(self) -> strawberry.ID:
        return self._channel.parent

    @strawberry.field(description="List of linked channel IDs")
    def links(self) -> list[strawberry.ID] | None:
        self._channel.links

    @strawberry.field(description="Get the description of the channel.")
    def description(self) -> str:
        return self._channel.description

    @strawberry.field(description="Check if the channel is temporary.")
    def temporary(self) -> bool:
        return self._channel.temporary

    @strawberry.field(description="Position of the channel which is used in Client for sorting.")
    def position(self) -> int:
        return self._channel.position


@strawberry.input
class UserStateInput:
    id: strawberry.ID
    channel: Optional[strawberry.ID] = None
    mute: Optional[bool] = None
    deaf: Optional[bool] = None
    suppress: Optional[bool] = None


@strawberry.type
class User:
    _user: strawberry.Private[MumbleServer.User]
    _server: strawberry.Private[MumbleServer.ServerPrx]

    def __init__(self, user: MumbleServer.User, server: MumbleServer.ServerPrx):
        self._user = user
        self._server = server

    @strawberry.field(description="Session ID. This identifies the connection to the server.")
    def id(self) -> strawberry.ID:
        return self._user.session

    @strawberry.field(description="Registered User ID. -1 if the user is anonymous.")
    def user_id(self) -> strawberry.ID:
        return self._user.userid

    @strawberry.field(description="The name of the user.")
    def name(self) -> str:
        return self._user.name

    @strawberry.field(description="User comment. Shown as tooltip for this user.")
    def comment(self) -> str:
        return self._user.comment

    @strawberry.field(description="Channel ID the user is in. Matches `Channel.id`.")
    def channel(self) -> strawberry.ID:
        return self._user.channel

    @strawberry.field(description="Is user muted by the server?")
    def mute(self) -> bool:
        return self._user.mute

    @strawberry.field(description="Is the user self-muted?")
    def self_mute(self) -> bool:
        return self._user.selfMute

    @strawberry.field(description="Is user deafened by the server? If true, this implies mute.")
    def deaf(self) -> bool:
        return self._user.deaf

    @strawberry.field(description="Is the user self-deafened? If true, this implies mute.")
    def self_deaf(self) -> bool:
        return self._user.selfDeaf

    @strawberry.field(description="Is user suppressed by the server? If true, this implies mute.")
    def suppress(self) -> bool:
        return self._user.suppress

    @strawberry.field(description="Is the User recording?")
    def recording(self) -> bool:
        return self._user.selfDeaf

    @strawberry.field(description="Seconds user has been online.")
    def online_secs(self) -> int:
        return self._user.onlinesecs

    @strawberry.field(description="Idle time. This is how many seconds it is since the user last spoke. Other activity is not counted.")
    def idle_secs(self) -> int:
        return self._user.idlesecs

    @strawberry.field(description="Average transmission rate in bytes per second over the last few seconds.")
    def bytes_per_sec(self) -> int:
        return self._user.bytespersec

    @strawberry.field(description="Client OS.")
    def os(self) -> str:
        return self._user.os

    @strawberry.field(description="Client OS Version.")
    def os_version(self) -> str:
        return self._user.osversion

    @strawberry.field(description="Client version.")
    def version(self) -> str:
        return self._user.version or self._user.version2

    @strawberry.field(description="Client release. For official releases, this equals the version. For snapshots and git compiles, this will be something else.")
    def release(self) -> str:
        return self._user.release

    @strawberry.field(description="Client address.")
    def address(self) -> str:
        return address_tuple_to_ipv6(self._user.address)

    @strawberry.field(description="Base64 encoded texture data URI. Only available for registered users.")
    def texture(self) -> str | None:
        # ServerPrx.getTexture is only for registered users.
        if self._user.userid == -1:
            return None

        server_id = self._server.id()
        user_id = self._user.userid

        return get_texture_cache(server_id, user_id) or set_texture_cache(
            server_id,
            user_id,
            self._server.getTexture(user_id)
        )


@strawberry.type(description="Event when a user sends a text message.")
class TextMessageEvent:
    _user: strawberry.Private[MumbleServer.User]
    _message: strawberry.Private[MumbleServer.TextMessage]
    _server: strawberry.Private[MumbleServer.ServerPrx]

    def __init__(self, user: MumbleServer.User, message: MumbleServer.TextMessage, server: MumbleServer.ServerPrx):
        self._user = user
        self._message = message
        self._server = server

    @strawberry.field(description="The user who sent the message.")
    def user_id(self) -> strawberry.ID:
        return self._user.userid

    @strawberry.field(description="The contents of the message.")
    def text(self) -> str:
        return self._message.text

    @strawberry.field(description="The server this message was sent to.")
    def server_id(self) -> strawberry.ID:
        return self._server.id()

    @strawberry.field(description="Channels who were sent this message. Matches `Channel.id`.")
    def channel_ids(self) -> list[strawberry.ID]:
        return self._message.channels

    @strawberry.field(description="Sessions (connected users) who were sent this message.")
    def session_ids(self) -> list[strawberry.ID]:
        return self._message.sessions


@strawberry.enum
class UserChangeType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    STATE_CHANGED = "state_changed"


@strawberry.type(description="Event when a user changes their state.")
class UserChangeEvent:
    changeType: UserChangeType

    _server: strawberry.Private[MumbleServer.ServerPrx]
    _user: strawberry.Private[MumbleServer.User]

    def __init__(self, changeType: UserChangeType, user: MumbleServer.User, server: MumbleServer.ServerPrx):
        self.changeType = changeType
        self._user = user
        self._server = server

    @strawberry.field(description="The user who changed their state.")
    def user(self) -> User:
        return User(self._user, self._server)

    @strawberry.field(description="The server this user is connected to.")
    def server_id(self) -> strawberry.ID:
        return self._server.id()


@strawberry.enum
class ChannelChangeType(Enum):
    CREATED = "created"
    REMOVED = "removed"
    STATE_CHANGED = "state_changed"


@strawberry.type(description="Event when a channel changes its state.")
class ChannelChangeEvent:
    changeType: ChannelChangeType

    _channel: strawberry.Private[MumbleServer.Channel]
    _server: strawberry.Private[MumbleServer.ServerPrx]

    def __init__(self, changeType: ChannelChangeType, channel: MumbleServer.Channel, server: MumbleServer.ServerPrx):
        self.changeType = changeType
        self._channel = channel
        self._server = server

    @strawberry.field(description="The channel that changed its state.")
    def channel(self) -> Channel:
        return Channel(self._channel)

    @strawberry.field(description="The parent server for this channel.")
    def server_id(self) -> strawberry.ID:
        return self._server.id()
