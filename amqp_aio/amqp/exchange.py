from amqp_aio.amqp.amqp_types import NoField, ShortString, Boolean, FieldTable
from amqp_aio.amqp.base_frame import FrameField
from amqp_aio.amqp.consts import EXCHANGE_CLASS_ID, EXCHANGE_DECLARE_ID, \
    EXCHANGE_DECLARE_OK_ID, EXCHANGE_DELETE_ID, EXCHANGE_DELETE_OK_ID
from amqp_aio.amqp.frames import MethodArguments, MethodFrame, Frame


class ExchangeMethod(MethodArguments):
    method_id = None
    class_id = EXCHANGE_CLASS_ID

    @classmethod
    def declare(cls, **arguments):
        return Frame.from_frame(MethodFrame(
            class_id=cls.class_id,
            method_id=cls.method_id,
            arguments=cls(**arguments)
        ))


class Declare(ExchangeMethod):
    method_id = EXCHANGE_DECLARE_ID

    reserved_1 = FrameField(NoField)
    exchange = FrameField(ShortString)
    type = FrameField(ShortString)
    passive = FrameField(Boolean)
    durable = FrameField(Boolean)
    reserved_2 = FrameField(NoField)
    reserved_3 = FrameField(NoField)
    no_wait = FrameField(Boolean)
    arguments = FrameField(FieldTable)

    class Meta:
        parsing_order = [
            'reserved_1', 'exchange', 'type', 'passive', 'durable',
            'reserved_2', 'reserved_3', 'no_wait', 'arguments'
        ]


class DeclareOK(ExchangeMethod):
    method_id = EXCHANGE_DECLARE_OK_ID


class Delete(ExchangeMethod):
    method_id = EXCHANGE_DELETE_ID

    reserved_1 = FrameField(NoField)
    exchange = FrameField(ShortString)
    if_unused = FrameField(Boolean)
    no_wait = FrameField(Boolean)

    class Meta:
        parsing_order = [
            'reserved_1', 'exchange', 'if_unused', 'no_wait'
        ]


class DeleteOK(ExchangeMethod):
    method_id = EXCHANGE_DELETE_OK_ID
