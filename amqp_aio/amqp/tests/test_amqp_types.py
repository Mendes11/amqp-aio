import struct
from datetime import datetime
from decimal import Decimal

import pytest

from amqp_aio.amqp.amqp_types import Octet, Boolean, ShortShortInt, \
    ShortShortUint, ShortInt, ShortUint, LongInt, LongUint, LongLongInt, \
    LongLongUint, Float, Double, DecimalValue, ShortString, LongString, \
    FieldArray, FieldTable, NoField, Timestamp


def test_octet_from_bytes():
    expected = Octet(5)
    value, remaining = Octet.from_bytes(b'\x05\x09\xdc')
    assert value == expected
    assert remaining == b'\x09\xdc'


def test_octet_from_bytes_wrong_size():
    with pytest.raises(struct.error):
        Octet.from_bytes(b'')


@pytest.mark.parametrize(
    ("cls", 'bytes_value', "expected", "expected_remaining"),
    [
        (Octet, b'\x05\x09\xdc', Octet(5), b'\x09\xdc'),
        (Boolean, b'\x01\x09\xdc', Boolean(True), b'\x09\xdc'),
        (ShortShortInt, b'\xff', ShortShortInt(-1), b''),
        (ShortShortUint, b'\xff\xdd', ShortShortUint(255), b'\xdd'),
        (ShortInt, b'\x00"\x03\xff', ShortInt(34), b'\x03\xff'),
        (ShortUint, b'\x03\xde', ShortUint(990), b''),
        (LongInt, b'\xff\xff\xff\x00', LongInt(-256), b''),
        (LongUint, b'\xff\xff\xff\x00\xff\xff', LongUint(4294967040), b'\xff\xff'),
        (LongLongInt, b'\xff\xff\xff\x00\xff\xff\xff\x00\x01\x02',
         LongLongInt(-1095216660736), b'\x01\x02'),
        (LongLongUint, b'\xff\xff\xff\x00\xff\xff\xff\x00\x01\x02',
         LongLongUint(18446742978492890880), b'\x01\x02'),
        (Float, b'B\x05Q\xec\xdd\xcc', Float(33.33), b'\xdd\xcc'),
        (Double, b'@@\xaa=p\xa3\xd7\n\xdd\xcc', Double(33.33), b'\xdd\xcc'),
        (DecimalValue, b'\x02\x00\x01\xe2@\xff\xff',
         DecimalValue(Decimal('1234.56')), b'\xff\xff'),
        (ShortString, b'\x04test\xff\xcc', ShortString('test'), b'\xff\xcc'),
        (LongString, b'\x00\x00\x00\x04test\xff\xcc', LongString('test'),
         b'\xff\xcc'),
        (FieldArray, b'\x00\x00\x00\x05u\x00\x02t\x01',
         FieldArray([ShortUint(2), Boolean(True)]), b''),
        (FieldTable,
         b'\x00\x00\x00\x10\x04testu\x00\x02\x05test2t\x01',
         FieldTable({'test': ShortUint(2), "test2": Boolean(True)}), b''),
        (NoField, b'\xff\xcc', NoField(), b'\xff\xcc'),
        (Timestamp, b'\x00\x00\x00\x00_\xee\x900\xff\xcc',
         Timestamp(datetime(2021, 1, 1)), b'\xff\xcc')
    ]
)
def test_from_bytes(cls, bytes_value, expected, expected_remaining):
    value, remaining = cls.from_bytes(bytes_value)
    if isinstance(value, (Float, Double)):
        assert round(value.value, 3) == round(expected.value, 3)
    else:
        assert value == expected
    assert remaining == expected_remaining


@pytest.mark.parametrize(
    ("expected", "obj"),
    [
        (b'\x05', Octet(5)),
        (b'\x01', Boolean(True)),
        (b'\xff', ShortShortInt(-1)),
        (b'\xff', ShortShortUint(255)),
        (b'\x00"', ShortInt(34)),
        (b'\x03\xde', ShortUint(990)),
        (b'\xff\xff\xff\x00', LongInt(-256)),
        (b'\xff\xff\xff\x00', LongUint(4294967040)),
        (b'\xff\xff\xff\x00\xff\xff\xff\x00',
         LongLongInt(-1095216660736)),
        (b'\xff\xff\xff\x00\xff\xff\xff\x00',
         LongLongUint(18446742978492890880)),
        (b'B\x05Q\xec', Float(33.33)),
        (b'@@\xaa=p\xa3\xd7\n', Double(33.33)),
        (b'\x02\x00\x01\xe2@',
         DecimalValue(Decimal('1234.56'))),
        (b'\x04test', ShortString('test')),
        (b'\x00\x00\x00\x04test', LongString('test')),
        (b'\x00\x00\x00\x05u\x00\x02t\x01',
         FieldArray([ShortUint(2), Boolean(True)])),
        (b'\x00\x00\x00\x10\x04testu\x00\x02\x05test2t\x01',
         FieldTable({'test': ShortUint(2), "test2": Boolean(True)})),
        (b'', NoField()),
        (b'\x00\x00\x00\x00_\xee\x900', Timestamp(datetime(2021, 1, 1)))
    ]
)
def test_to_bytes(expected, obj):
    assert obj.to_bytes() == expected
