from amqp_aio.amqp.amqp_types import AMQPType


def is_amqp_type(obj):
    return issubclass(obj, AMQPType)
