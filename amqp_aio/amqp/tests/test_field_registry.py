import pytest

from amqp_aio.amqp.amqp_types import FieldRegistry, ShortString, LongInt, \
    AMQPType


@pytest.fixture
def registry():
    return FieldRegistry({"c": ShortString('test'), 'd': LongInt(1)})


def test_field_registry_add_new_field(registry):
    registry.register_field("f", AMQPType)


def test_field_registry_add_not_amqp_type(registry):
    with pytest.raises(TypeError):
        registry.register_field("f", int)


def test_field_registry_get_field(registry):
    assert isinstance(registry['c'], ShortString)
    assert isinstance(registry['d'], LongInt)


def test_field_registry_field_not_found(registry):
    with pytest.raises(KeyError):
        _ = registry['a']