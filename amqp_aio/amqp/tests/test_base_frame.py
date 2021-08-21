import pytest

from amqp_aio.amqp.amqp_types import Octet, ShortInt, LongInt, ShortString, \
    FieldTable, LongString
from amqp_aio.amqp.base_frame import BaseFrame, FrameField, FrameSelectorField


def frame_selector(frame):
    if frame.field_1 == 1:
        return Frame2
    return Frame3


class Frame(BaseFrame):
    field_1 = FrameField(Octet)
    field_2 = FrameSelectorField(frame_selector)
    field_3 = FrameField(ShortInt)

    class Meta:
        parsing_order = ['field_1', 'field_3', 'field_2']


class Frame2(BaseFrame):
    field_1 = FrameField(ShortString)
    class Meta:
        parsing_order = ['field_1']


class Frame3(BaseFrame):
    size = FrameField(ShortInt)
    field_1 = FrameField(FieldTable)

    def validate_size(self, value, previous):
        return len(previous)

    class Meta:
        parsing_order = ['size', 'field_1']


def test_frames_order():
    expected_order = ['field_1', 'field_3', 'field_2']
    fields_order = [name for name, _ in Frame()._fields]
    assert fields_order == expected_order

def test_frames_fields_replaced():
    assert Frame().field_1 is None
    assert Frame().field_2 is None
    assert Frame().field_3 is None

def test_frames_fields_serialize_empty():
    with pytest.raises(ValueError):
        Frame2().to_bytes()


def test_frame_2_to_bytes():
    data = Frame2(field_1='TestString').to_bytes()
    assert data == b'\x0ATestString'

def test_frame_to_bytes():
    f = Frame(
        field_1=1,
        field_2=Frame2(
            field_1='TestString'
        ),
        field_3=10
    )
    # Field 1 | Field 3 | Field 2
    assert f.to_bytes() == b'\x01\x00\x0A\x0ATestString'


def test_frame_3_to_bytes_dict_wrong_types():
    with pytest.raises(TypeError):
        Frame3(field_1={'test': 10, 'test2': 'test'}).to_bytes()


def test_frame_3_to_bytes():
    f = Frame3(
        field_1={'test': ShortInt(10), 'test2': LongString('test')}
    )
    # Table has 24 bytes, so size variable will have a value of 24.
    assert f.to_bytes() == (
        b'\x00\x1B\x00\x00\x00\x17\x04testU\x00\x0A'
        b'\x05test2S\x00\x00\x00\x04test'
    )

def test_frame_field_with_default_value():
    class Frame(BaseFrame):
        field_1 = FrameField(ShortInt, default=1)
        field_2 = FrameField(ShortString)

    f = Frame()
    assert f.field_1 == 1
    assert f.field_2 is None


def test_frame3_from_bytes():
    f, remaining = Frame3.from_bytes(
        b'\x00\x1B\x00\x00\x00\x17\x04testU\x00\x0A\x05test2S\x00\x00\x00'
        b'\x04test'
    )
    assert isinstance(f, Frame3)
    assert remaining == b''
    assert f.size == 27
    assert f.field_1 == {
        'test': 10, 'test2': 'test'
    }

def test_frame_from_bytes_selector():
    f, remaining = Frame.from_bytes(
        b'\x01\x00\x0A\x04test\xff\xcc'
    )
    assert isinstance(f, Frame)
    assert remaining == b'\xff\xcc'
    assert f.field_1 == 1
    assert f.field_3 == 10
    assert isinstance(f.field_2, Frame2)
    assert f.field_2.field_1 == 'test'
