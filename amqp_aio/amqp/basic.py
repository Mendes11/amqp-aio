from amqp_aio.amqp.amqp_types import ShortString, LongInt, ShortInt, Boolean, \
    NoField, FieldTable, LongLongInt
from amqp_aio.amqp.base import AMQPObject


class ContentHeaderFrame:
    """
    Frame Details:
     - Inside payload frame:

    +----------+---------+-------------+----------------+----------------------
    | class-id | weight  |  body size  | property flags | property list...
    +----------+---------+-------------+----------------+----------------------
      2 Bytes  | 2 Bytes |   8 Bytes   |    2 Bytes     |    remainder...

    """
    class_id: ShortInt


class Qos(AMQPObject):
    prefetch_size: LongInt = 1
    prefetch_count: ShortInt = 2
    is_global: Boolean = 3


class QosOK(AMQPObject):
    ...

class Consume(AMQPObject):
    reserved_1: NoField = 1
    queue: ShortString = 2
    consumer_tag: ShortString = 3
    no_local: Boolean = 4
    no_ack: Boolean = 5
    exclusive: Boolean = 6
    no_wait: Boolean = 7
    arguments: FieldTable = 8


class ConsumeOK(AMQPObject):
    consumer_tag: ShortString = 1


class Cancel(AMQPObject):
    consumer_tag: ShortString = 1
    no_wait: Boolean = 2


class CancelOK(AMQPObject):
    consumer_tag: ShortString = 1


class Publish(AMQPObject):
    reserved_1: NoField = 1
    exchange: ShortString = 2
    routing_key: ShortString = 3
    mandatory: Boolean = 4
    immediate: Boolean = 5


class Return(AMQPObject):
    reply_code: ShortInt = 1
    reply_text: ShortString = 2
    redelivered: Boolean = 3
    exchange: ShortString = 4
    routing_key: ShortString = 5


class Deliver(AMQPObject):
    consumer_tag: ShortString = 1
    delivery_tag: LongLongInt = 2
    redelivered: Boolean = 3
    exchange: ShortString = 4
    routing_key: ShortString = 5


class Get(AMQPObject):
    reserved_1: NoField = 1
    queue: ShortString = 2
    no_ack: Boolean = 3

class GetOK(AMQPObject):
    delivery_tag: LongLongInt = 1
    redelivered: Boolean = 2
    exchange: ShortString = 3
    routing_key: ShortString = 4
    message_count: LongInt = 5

class GetEmpty(AMQPObject):
    ...

class Ack(AMQPObject):
    delivery_tag: LongLongInt = 1
    multiple: Boolean = 2

class Reject(AMQPObject):
    delivery_tag: LongLongInt = 1
    requeue: Boolean = 2

class RecoverAsync(AMQPObject):
    requeue: Boolean = 1

class Recover(AMQPObject):
    requeue: Boolean = 1


class RecoverOK(AMQPObject):
    ...

