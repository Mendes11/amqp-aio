from amqp_aio.amqp.amqp_types import NoField, ShortString, Boolean, FieldTable, \
    LongInt

from amqp_aio.amqp.base_frame import FrameField
from amqp_aio.amqp.consts import QUEUE_CLASS_ID, QUEUE_DECLARE_ID, \
    QUEUE_DECLARE_OK_ID, QUEUE_BIND_ID, QUEUE_BIND_OK_ID, QUEUE_UNBIND_ID, \
    QUEUE_UNBIND_OK_ID, QUEUE_PURGE_ID, QUEUE_PURGE_OK_ID, QUEUE_DELETE_ID, \
    QUEUE_DELETE_OK_ID
from amqp_aio.amqp.frames import MethodArguments, MethodFrame, Frame


class QueueMethod(MethodArguments):
    class_id = QUEUE_CLASS_ID
    method_id = None

    @classmethod
    def declare(cls, **arguments):
        return Frame.from_frame(MethodFrame(
            class_id=cls.class_id,
            method_id=cls.method_id,
            arguments=cls(**arguments)
        ))


class Declare(QueueMethod):
    method_id = QUEUE_DECLARE_ID

    reserved_1 = FrameField(NoField)
    queue = FrameField(ShortString)
    passive = FrameField(Boolean)
    durable = FrameField(Boolean)
    exclusive = FrameField(Boolean)
    auto_delete = FrameField(Boolean)
    no_wait = FrameField(Boolean)
    arguments = FrameField(FieldTable)

    class Meta:
        parsing_order = [
            'reserved_1', 'queue', 'passive', 'durable', 'exclusive',
            'auto_delete', 'no_wait', 'arguments'
        ]


class DeclareOK(QueueMethod):
    method_id = QUEUE_DECLARE_OK_ID

    queue = FrameField(ShortString)
    message_count = FrameField(LongInt)
    consumer_count = FrameField(LongInt)

    class Meta:
        parsing_order = [
            'queue', 'message_count', 'consumer_count'
        ]


class Bind(QueueMethod):
    method_id = QUEUE_BIND_ID

    reserved_1 = FrameField(NoField)
    queue = FrameField(ShortString)
    exchange = FrameField(ShortString)
    routing_key = FrameField(ShortString)
    no_wait = FrameField(Boolean)
    arguments = FrameField(FieldTable)

    class Meta:
        parsing_order = [
            'reserved_1', 'queue', 'exchange', 'routing_key',
            'no_wait', 'arguments'
        ]


class BindOK(QueueMethod):
    method_id = QUEUE_BIND_OK_ID


class Unbind(QueueMethod):
    method_id = QUEUE_UNBIND_ID

    reserved_1 = FrameField(NoField)
    queue = FrameField(ShortString)
    exchange = FrameField(ShortString)
    routing_key = FrameField(ShortString)
    arguments = FrameField(FieldTable)

    class Meta:
        parsing_order = [
            'reserved_1', 'queue', 'exchange', 'routing_key', 'arguments'
        ]


class UnbindOK(QueueMethod):
    method_id = QUEUE_UNBIND_OK_ID


class Purge(QueueMethod):
    method_id = QUEUE_PURGE_ID

    reserved_1 = FrameField(NoField)
    queue = FrameField(ShortString)
    no_wait = FrameField(Boolean)

    class Meta:
        parsing_order = [
            'reserved_1', 'queue', 'no_wait'
        ]


class PurgeOK(QueueMethod):
    method_id = QUEUE_PURGE_OK_ID


class Delete(QueueMethod):
    method_id = QUEUE_DELETE_ID

    reserved_1 = FrameField(NoField)
    queue = FrameField(ShortString)
    if_unused = FrameField(Boolean)
    if_empty = FrameField(Boolean)
    no_wait = FrameField(Boolean)

    class Meta:
        parsing_order = [
            'reserved_1', 'queue', 'if_unused', 'if_empty', 'no_wait'
        ]


class DeleteOK(QueueMethod):
    method_id = QUEUE_DELETE_OK_ID

    message_count = FrameField(LongInt)
