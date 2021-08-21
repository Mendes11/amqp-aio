from amqp_aio.amqp.amqp_types import Boolean, ShortInt, ShortString

from amqp_aio.amqp.base_frame import FrameField
from amqp_aio.amqp.consts import CHANNEL_CLASS_ID, CHANNEL_OPEN_ID, \
    CHANNEL_OPEN_OK_ID, CHANNEL_FLOW_ID, CHANNEL_FLOW_OK_ID, CHANNEL_CLOSE_ID, \
    CHANNEL_CLOSE_OK_ID
from amqp_aio.amqp.frames import MethodArguments, MethodFrame, Frame


class ChannelMethod(MethodArguments):
    method_id = None
    class_id = CHANNEL_CLASS_ID

    @classmethod
    def declare(cls, **arguments):
        return Frame.from_frame(MethodFrame(
            class_id=cls.class_id,
            method_id=cls.method_id,
            arguments=cls(**arguments)
        ))


class Open(ChannelMethod):
    method_id = CHANNEL_OPEN_ID


class OpenOk(ChannelMethod):
    method_id = CHANNEL_OPEN_OK_ID


class Flow(ChannelMethod):
    method_id = CHANNEL_FLOW_ID

    active = FrameField(Boolean)


class FlowOK(ChannelMethod):
    method_id = CHANNEL_FLOW_OK_ID

    active = FrameField(Boolean)


class Close(ChannelMethod):
    method_id = CHANNEL_CLOSE_ID

    reply_code = FrameField(ShortInt)
    reply_text = FrameField(ShortString)
    class_id = FrameField(ShortInt)
    method_id_ = FrameField(ShortInt)

    class Meta:
        parsing_order = [
            'reply_code', 'reply_text', 'class_id', 'method_id_'
        ]


class CloseOK(ChannelMethod):
    method_id = CHANNEL_CLOSE_OK_ID
