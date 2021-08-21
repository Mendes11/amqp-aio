import asyncio
import platform
import struct
from datetime import datetime
from typing import Tuple

from pika import spec

from amqp_aio.amqp import connection
from amqp_aio.amqp.amqp_types import FieldTable, ShortString, LongString, \
    ShortInt, Boolean
from amqp_aio.amqp.consts import PROTOCOL_HEADER, VERSION, FRAME_END, \
    LIB_VERSION, PRODUCT
from amqp_aio.amqp.exceptions import ProtocolError, FrameEndError, \
    AMQPException, raise_error_from_server
from amqp_aio.amqp.frames import Frame, FrameHeader, MethodFrame, \
    HeartbeatFrame
from amqp_aio.amqp.negotiator import ProtocolNegotiator
from amqp_aio.frame_router import FrameRouter


class AMQPConnection():
    """
    AMQP Protocol Connection Class for Client Side

    Exposes the expected methods from the protocol and handles all bound
    channels.
    """
    class_id = 10
    default_negotiator = ProtocolNegotiator
    default_frame_router = FrameRouter

    def __init__(self, conn, negotiator=None, heartbeat=None,
                 frame_router=None):
        """
        Receives an instance responsible for the transfer of data between
        peers.
        :param conn: A Connection Instance
        :param negotiator: Negotiator class object (ProtocolNegotiator as
        default)
        :param int heartbeat: Desired delay between Heartbeats
        """
        self.conn = conn
        self.last_send_dt = datetime.utcnow()
        self.missed_heartbeats = 0
        self.heartbeat_task = None
        self._running = False
        self._binds = {}
        self.mechanism = None
        self.locale = None
        self._connection_opened = False
        self.server_properties = {}
        self.vhost = "/"
        self.negotiator = negotiator or self.default_negotiator()
        self.router = frame_router or self.default_frame_router()
        self.heartbeat = heartbeat
        self.router.register_route(0, connection.Start, self._handle_start_frame)
        self.router.register_route(0, connection.Tune, self._handle_tune_frame)
        self.router.register_route(0, connection.OpenOK, self._handle_open_ok)
        self.router.register_route(0, connection.Close, self._on_close_requested)
        self.router.register_route(0, HeartbeatFrame, self._handle_server_heartbeat)

    async def _send_to_server(self, data):
        if hasattr(data, 'to_bytes'):
            # is an object
            data = data.to_bytes()
        msg = data + FRAME_END
        await self.conn.send(msg)
        self.last_send_dt = datetime.utcnow()

    async def _send_start_ok(self):
        frame = connection.StartOk.declare(
            channel=0,
            locale=self.locale,
            client_properties={
                "product": LongString(PRODUCT),
                'version': LongString(LIB_VERSION),
                "capabilities": FieldTable({
                    'authentication_failure_close': Boolean(True),
                    'basic.nack': Boolean(True),
                    'connection.blocked': Boolean(True),
                    'consumer_cancel_notify': Boolean(True),
                    'publisher_confirms': Boolean(True)
                }),
                'platform': LongString(
                    'Python {}'.format(platform.python_version())
                ),
                "information": LongString(
                    "https://github.com/Mendes11/amqp-aio"
                )
            },
            mechanism=self.mechanism,
            response='\0guest\0guest' # TODO Configurable
        )
        await self._send_to_server(frame)

    async def _wait_connect_response(self):
        content = await self.conn.recv(5)
        if content == b"AMQP\x00":
            supported_version = await self.conn.recv(3)
            supported_version = struct.unpack(">BBB", supported_version)
            raise ProtocolError(
                f"Target server does not support {VERSION} version. "
                f"Supported Version is: {supported_version}"
            )

        # If version is accepted, we then parse the connection-start response
        # Obtaining the remaining bytes for our 7 Bytes Header Frame
        content += await self.conn.recv(2)
        f, remaining = await self.parse_frame(content)

        start = f.payload.arguments
        assert isinstance(start, connection.Start), (
            f'Server Returned a wrong Frame. expected Start, received '
            f'{type(start)}'
        )
        return start

    async def connect(self, blocking=False):
        if not self.conn.is_connected:
            await self.conn.connect()

        _version = struct.pack(">BBB", *VERSION)
        await self.conn.send(PROTOCOL_HEADER + _version)
        if blocking:
            await self._run()
        else:
            asyncio.ensure_future(self._run())

    async def _handle_start_frame(self, frame: connection.Start):
        self.mechanism = self.negotiator.negotiate_auth_mechanism(
            "PLAIN", frame.mechanisms.split(" ")
        )
        self.locale = 'en_US'
        self.server_capabilities = frame.server_properties
        await self._send_start_ok()

    async def _handle_tune_frame(self, frame: connection.Tune):
        """
        Negotiates the tuning parameters and sends the desired values back to
        the server
        :param int channel: Channel (expected to be zero)
        :param connection.Tune frame: Tune Frame arguments
        """
        self.max_frame_length = self.negotiator.negotiate_numeric(
            0, frame.frame_max # use the server proposed value
        )
        self.max_channels = self.negotiator.negotiate_numeric(
            0, frame.channel_max # use the server proposed value
        )
        self.heartbeat = self.negotiator.negotiate_numeric(
            self.heartbeat, frame.heartbeat
        )
        response = connection.TuneOK.declare(
            channel=0, frame_max=self.max_frame_length,
            channel_max=self.max_channels, heartbeat=self.heartbeat
        )
        await self._send_to_server(response)

        open = connection.Open.declare(
            channel=0, virtual_host=self.vhost
        )
        await self._send_to_server(open)

    async def _handle_open_ok(self, frame: connection.OpenOK):
        self._connection_opened = True
        print("Successfully connected to VHost: {}".format(self.vhost))
        self.heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())

    async def _on_close_requested(self, frame: connection.Close):
        ok = connection.CloseOK.declare(channel=0)
        await self._send_to_server(ok)
        raise_error_from_server(frame.reply_code, frame.reply_text)

    async def _handle_server_heartbeat(self, frame: HeartbeatFrame):
        print("Server Heartbeat Received")
        self.missed_heartbeats = 0

    async def _on_frame_received(self, frame: Frame):
        try:
            await self.router.route_frame(frame)
        except KeyError:
            print("Frame {} has no router. Skipping it.".format(frame))

    async def _heartbeat_loop(self):
        print("Initiating Heartbeat Loop")
        while self._running:
            await asyncio.sleep(self.heartbeat // 2)
            seconds_without_send = (
                    datetime.utcnow() - self.last_send_dt
            ).total_seconds()
            if seconds_without_send > self.heartbeat:
                heartbeat = Frame.from_frame(HeartbeatFrame(), channel=0)
                await self._send_to_server(heartbeat)

    async def _run(self):
        """
        Read Frames until the connection closes.
        :return:
        """
        self._running = True
        while self._running:
            try:
                header = await asyncio.wait_for(
                    self.conn.recv(7), timeout=self.heartbeat
                )
            except asyncio.TimeoutError:
                print("Read Timed-out increasing missed heartbeats count")
                self.missed_heartbeats += 1
                if self.missed_heartbeats > 4:
                    await self.close()
                    raise ConnectionAbortedError(
                        "Server missed heartbeats. Closing connection"
                    )
                continue

            if header.startswith(b"AMQP"):
                # Some Protocol Version Error.
                header += await self.conn.recv(1)
                supported_version = struct.unpack(">BBB", header[-3:])
                raise ProtocolError(
                    f"Target server does not support {VERSION} version. "
                    f"Supported Version is: {supported_version}"
                )
            frame, remaining = await self.parse_frame(header)
            assert remaining == b'', 'Remaining of {} is not empty: {}'.format(
                frame, remaining
            )
            # remaining should always be empty
            await self._on_frame_received(frame)

    async def parse_frame(self, header) -> Tuple[Frame, bytes]:
        frame_header, remaining = FrameHeader.from_bytes(header)
        payload = await self.conn.recv(frame_header.size + 1)
        if not payload.endswith(FRAME_END):
            raise FrameEndError(
                "Expected Frame-End not found after reading the whole "
                "frame data."
            )
        payload = payload.rstrip(FRAME_END)
        return Frame.from_bytes(header + payload)

    async def close(self):
        self._running = False


async def _get_connection(
        host: str, port: int, ssl=None, loop=None
):
    if loop is None:
        loop = asyncio.get_event_loop()
    return await asyncio.open_connection(
        host, port=port, loop=loop, ssl=ssl,
    )


class TCPConnection:
    """
    A TCP Connection Instance with an AMQP Server.

    This is the Transport Layer of our AMQP Protocol implementation
    """

    def __init__(self, host, port=None, ssl=None):
        self._host = host
        self._port = port or 5672
        self.ssl = ssl
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self.is_connected = False

    async def send(self, data):
        if isinstance(data, str):
            data = data.encode()

        self._writer.write(data)

    async def recv(self, size, timeout=None):
        return await asyncio.wait_for(
            self._reader.readexactly(size), timeout
        )

    async def connect(self, loop=None, timeout=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._reader, self._writer = await asyncio.wait_for(
            _get_connection(
                self.host, port=self.port, ssl=self.ssl, loop=loop
            ), timeout
        )
        self.is_connected = True

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
