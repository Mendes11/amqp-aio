from amqp_aio.amqp.amqp_types import Octet, ShortInt, LongInt
from amqp_aio.amqp.base_frame import BaseFrame, FrameField, FrameSelectorField
from amqp_aio.amqp.consts import METHOD_TYPE, HEARTBEAT_TYPE
from amqp_aio.amqp.selectors import select_method_frame


def select_amqp_frame(frame):
    if frame.frame_type == METHOD_TYPE:
        return MethodFrame
    if frame.frame_type == HEARTBEAT_TYPE:
        return HeartbeatFrame


class FrameHeader(BaseFrame):
    """
    Parse Frame Header only, not failing due to lack of a payload.

    Use this class to discover the payload size, if you want to ensure the
    frame data is completed before trying to parse it.
    """
    frame_type = FrameField(Octet)
    channel = FrameField(ShortInt)
    size = FrameField(LongInt)

    class Meta:
        parsing_order = ['frame_type', 'channel', 'size']


class Frame(FrameHeader):
    payload = FrameSelectorField(selector=select_amqp_frame)

    def validate_size(self, value, previous):
        return len(previous)

    @classmethod
    def from_frame(cls, frame, channel):
        assert isinstance(frame, BaseFrame), (
            f'{frame} must be a subclass of BaseFrame class'
        )
        frame_type = None
        if isinstance(frame, MethodFrame):
            frame_type = METHOD_TYPE
        elif isinstance(frame, HeartbeatFrame):
            frame_type = HEARTBEAT_TYPE
        return Frame(frame_type=frame_type, payload=frame, channel=channel)

    def __str__(self):
        return 'Frame<{}>'.format(str(self.payload))

    def __repr__(self):
        return str(self)

    class Meta:
        parsing_order = ['frame_type', 'channel', 'size', 'payload']


class MethodFrame(BaseFrame):
    class_id = FrameField(ShortInt)
    method_id = FrameField(ShortInt)
    arguments = FrameSelectorField(selector=select_method_frame)

    def __str__(self):
        return '{} Method'.format(type(self.arguments))

    def __repr__(self):
        return str(self)

    class Meta:
        parsing_order = ["class_id", "method_id", "arguments"]


class MethodArguments(BaseFrame):
    """
    Must be subclassed by all AMQP class methods
    """
    class_id = None
    method_id = None


class HeartbeatFrame(BaseFrame):
    ...