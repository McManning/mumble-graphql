import asyncio
import os
import Ice
import MumbleServer
from schema_types import ChannelChangeEvent, ChannelChangeType, TextMessageEvent, UserChangeEvent, UserChangeType
from events import text_message_events, user_change_events, channel_change_events


class MetaCallback(MumbleServer.MetaCallback):
    def __init__(self, adapter):
        self.adapter = adapter

    def started(self, server, current=None):
        """ Called when a server is started.

        The server is up and running when this event is sent,
        so all methods that need a running server will work.
        """
        server_cb = MumbleServer.ServerCallbackPrx.uncheckedCast(
            self.adapter.addWithUUID(ServerCallback(server, current.adapter))
        )

        server.addCallback(server_cb)

    def stopped(self, server, current=None):
        """ Called when a server is stopped.

        The server is already stopped when this event is sent,
        so no methods that need a running server will work.
        """
        pass


class ServerContextCallback(MumbleServer.ServerContextCallback):
    """Callback for injecting additional content into the Murmur context menu"""

    def __init__(self, server):
        self.server = server

    def contextAction(self, action, p, session, channel_id):
        print(action, p)


class ServerCallback(MumbleServer.ServerCallback):
    """Callback for Murmur server events for a distinct server"""
    _server: MumbleServer.ServerPrx
    _adapter: Ice.ObjectAdapter

    def __init__(self, server, adapter):
        self._adapter = adapter
        self._server = server

        # self.contextR = Murmur.ServerContextCallbackPrx.uncheckedCast(
        #     adapter.addWithUUID(ServerContextCallback(server))
        # )

    def userConnected(self, user, current=None):
        user_change_events.publish(
            UserChangeEvent(
                UserChangeType.CONNECTED,
                user,
                self._server
            )
        )

    def userDisconnected(self, user, current=None):
        user_change_events.publish(
            UserChangeEvent(
                UserChangeType.DISCONNECTED,
                user,
                self._server
            )
        )

    def userStateChanged(self, user, current=None):
        user_change_events.publish(
            UserChangeEvent(
                UserChangeType.STATE_CHANGED,
                user,
                self._server
            )
        )

    def userTextMessage(self, user, msg: MumbleServer.TextMessage, current=None):
        text_message_events.publish(
            TextMessageEvent(user, msg, self._server)
        )

    def channelCreated(self, channel, current=None):
        channel_change_events.publish(
            ChannelChangeEvent(
                ChannelChangeType.CREATED,
                channel,
                self._server
            )
        )

    def channelRemoved(self, channel, current=None):
        channel_change_events.publish(
            ChannelChangeEvent(
                ChannelChangeType.REMOVED,
                channel,
                self._server
            )
        )

    def channelStateChanged(self, channel, current=None):
        channel_change_events.publish(
            ChannelChangeEvent(
                ChannelChangeType.STATE_CHANGED,
                channel,
                self._server
            )
        )


class MumbleClient:
    """
    Communicator to a Mumble servers using Ice.
    """
    meta: MumbleServer.MetaPrx = None
    servers: list[MumbleServer.ServerPrx] = []
    comm: Ice.Communicator = None

    def __init__(self, host: str = 'localhost', port: int = 6502, secret: str = None):
        self.host = host
        self.port = port
        self.proxy = f'Meta:tcp -h {self.host} -p {self.port}'
        self.secret = secret

    def connect(self):
        try:
            props = Ice.createProperties()
            props.setProperty('Ice.ImplicitContext', 'Shared')
            props.setProperty('Ice.Default.EncodingVersion', '1.0')

            idd = Ice.InitializationData()
            idd.properties = props

            self.comm = Ice.initialize(idd)
            if self.secret:
                self.comm.getImplicitContext().put('secret', self.secret)

            base = self.comm.stringToProxy(self.proxy)
            self.meta = MumbleServer.MetaPrx.checkedCast(base)
            assert self.meta is not None

            self.servers = self.meta.getAllServers()
            print(f"Found {len(self.servers)} servers")

            self.bind_events()
            return self.meta

        except MumbleServer.InvalidSecretException as e:
            print(f"Invalid secret: {e}")
            return None
        except Exception as e:
            print(f"Error connecting to Mumble server: {e}")
            return None

    def bind_events(self):
        adapter = self.comm.createObjectAdapterWithEndpoints(
            'Callback.Client', 'tcp')

        # Attach event handlers for "meta" events (server start/stop)
        meta_cb = MumbleServer.MetaCallbackPrx.uncheckedCast(
            adapter.addWithUUID(MetaCallback(adapter))
        )

        adapter.activate()
        self.meta.addCallback(meta_cb)

        # Attach event handlers to all already running server instances
        for server in self.meta.getBootedServers():
            server_cb = MumbleServer.ServerCallbackPrx.uncheckedCast(
                adapter.addWithUUID(ServerCallback(server, adapter))
            )

            server.addCallback(server_cb)


_client = None


def get_mumble_client():
    global _client
    if _client is None:
        if os.environ.get('ICE_HOST') is None:
            raise KeyError('Missing required ICE_HOST envvar')

        _client = MumbleClient(
            host=os.environ.get('ICE_HOST'),
            port=os.environ.get('ICE_PORT') or 6502,
            secret=os.environ.get('ICE_SECRET')
        )
        _client.connect()
        print(f"Connected to Mumble server at {_client.host}:{_client.port}")

    return _client


def get_mumble_servers() -> list[MumbleServer.ServerPrx]:
    client = get_mumble_client()
    return client.servers or []


def get_mumble_server(server_id: str) -> MumbleServer.ServerPrx | None:
    client = get_mumble_client()
    for server in client.servers:
        if str(server.id()) == server_id:
            return server

    return None


def mumble_heartbeat():
    """Check and refresh the Mumble server connection."""
    client = get_mumble_client()
    for server in client.servers:
        try:
            server.id()
        except Ice.ConnectFailedException:
            print("Heartbeat: Connection closed, reconnecting...")
            client.connect()
            break
        except Exception as e:
            print(f"Heartbeat: Error: {e}")
            client.connect()
