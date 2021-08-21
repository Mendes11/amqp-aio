from amqp_aio.amqp.amqp_types import Octet, FieldTable, LongString, \
    ShortString, ShortInt, LongInt, Boolean
from amqp_aio.amqp.base_frame import FrameField
from amqp_aio.amqp.consts import CONNECTION_CLASS_ID, CONNECTION_START_ID, \
    CONNECTION_START_OK_ID, CONNECTION_SECURE_ID, CONNECTION_SECURE_OK_ID, \
    CONNECTION_TUNE_ID, CONNECTION_TUNE_OK_ID, CONNECTION_OPEN_ID, \
    CONNECTION_OPEN_OK_ID, CONNECTION_CLOSE_ID, CONNECTION_CLOSE_OK_ID
from amqp_aio.amqp.frames import MethodArguments, Frame, MethodFrame


class ConnectionMethod(MethodArguments):
    method_id = None
    class_id = CONNECTION_CLASS_ID

    @classmethod
    def declare(cls, channel, **arguments):
        return Frame.from_frame(MethodFrame(
            class_id=cls.class_id,
            method_id=cls.method_id,
            arguments=cls(**arguments)
        ), channel=channel)


class Start(ConnectionMethod):
    """
    Start Connection Negotiation
    Called from server after a start of connection
    """
    method_id = CONNECTION_START_ID
    version_major = FrameField(Octet)
    version_minor = FrameField(Octet)
    server_properties = FrameField(FieldTable)
    mechanisms = FrameField(LongString)
    locales = FrameField(LongString)

    class Meta:
        parsing_order = [
            'version_major', 'version_minor', 'server_properties',
            'mechanisms', 'locales'
        ]


class StartOk(ConnectionMethod):
    """
    Method called from client to server, after a Start method
    """
    method_id = CONNECTION_START_OK_ID

    client_properties = FrameField(FieldTable)
    mechanism = FrameField(ShortString)
    response = FrameField(LongString)
    locale = FrameField(ShortString)

    class Meta:
        parsing_order = [
            'client_properties', 'mechanism', 'response', 'locale'
        ]


class Secure(ConnectionMethod):
    method_id = CONNECTION_SECURE_ID

    challenge = FrameField(LongString)


class SecureOK(ConnectionMethod):
    method_id = CONNECTION_SECURE_OK_ID

    response = FrameField(LongString)


class Tune(ConnectionMethod):
    method_id = CONNECTION_TUNE_ID

    channel_max = FrameField(ShortInt)
    frame_max = FrameField(LongInt)
    heartbeat = FrameField(ShortInt)

    class Meta:
        parsing_order = ['channel_max', 'frame_max', 'heartbeat']


class TuneOK(ConnectionMethod):
    method_id = CONNECTION_TUNE_OK_ID

    channel_max = FrameField(ShortInt)
    frame_max = FrameField(LongInt)
    heartbeat = FrameField(ShortInt)

    class Meta:
        parsing_order = ['channel_max', 'frame_max', 'heartbeat']


class Open(ConnectionMethod):
    method_id = CONNECTION_OPEN_ID

    virtual_host = FrameField(ShortString)
    capabilities = FrameField(ShortString, default='')
    insist = FrameField(Boolean, default=True)

    class Meta:
        parsing_order = ['virtual_host', 'capabilities', 'insist']

class OpenOK(ConnectionMethod):
    method_id = CONNECTION_OPEN_OK_ID

    known_hosts = FrameField(ShortString, default='')


class Close(ConnectionMethod):
    method_id = CONNECTION_CLOSE_ID

    reply_code = FrameField(ShortInt)
    reply_text = FrameField(ShortString)
    class_id = FrameField(ShortInt)
    failure_method_id = FrameField(ShortInt)

    class Meta:
        parsing_order = [
            'reply_code', 'reply_text', 'class_id', 'failure_method_id'
        ]


class CloseOK(ConnectionMethod):
    method_id = CONNECTION_CLOSE_OK_ID
