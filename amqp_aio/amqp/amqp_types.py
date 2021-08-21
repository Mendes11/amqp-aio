import struct
from datetime import datetime
from decimal import Decimal
from typing import Tuple, Any, List, Dict, Union, ClassVar


class FieldRegistry:
    def __init__(self, fields: Dict[str, 'AMQPType'] = None):
        self.fields: Dict[str, 'AMQPType'] = fields or {}

    def register_field(self, char: str, field: 'AMQPType'):
        if not issubclass(field, AMQPType):
            raise TypeError(f"Field {field} is not an AMQPType type")
        self.fields[char] = field

    def __getitem__(self, item):
        return self.fields[item]

    def __call__(self, amqp_cls: ClassVar['AMQPType']) -> ClassVar['AMQPType']:
        if amqp_cls.type_str is not None:
            self.register_field(amqp_cls.type_str, amqp_cls)
        return amqp_cls


amqp_fields = FieldRegistry()


class AMQPType:
    """
    A type that has representation in bytes following the AMQP Protocol
    """
    value: Any
    type_str: str
    python_cls: Any

    def __init__(self, value: Any = None):
        self.value = value if value is not None else self.python_cls()

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        raise NotImplementedError()

    def to_bytes(self) -> bytes:
        raise NotImplementedError()

    def to_python(self):
        if isinstance(self.value, AMQPType):
            return self.value.to_python()
        return self.value

    def __eq__(self, other):
        return self.value == other


class FieldValue(AMQPType):
    value: AMQPType

    def __init__(self, value: AMQPType):
        if not isinstance(value, AMQPType):
            raise TypeError(
                "'value' must be an AMQPType object instance"
            )
        if isinstance(value, ShortString):
            # RabbitMQ and Qpid incompatibilities with the grammar used by
            # amqp (https://www.rabbitmq.com/amqp-0-9-1-errata.html#section_3)
            # Basically, ShortStrings aren't used for tables/arrays values
            value = LongString(value.value)

        self.value_cls = type(value)
        super(FieldValue, self).__init__(value)

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        # remaining[:1] instead of [0] due to it being converted to int if
        # the latest is done instead of the former
        type_character, remaining = data[:1], data[1:]
        field = amqp_fields[type_character.decode()]
        field_val, remaining = field.from_bytes(remaining)
        return cls(field_val), remaining

    def to_bytes(self) -> bytes:
        return self.value_cls.type_str.encode() + self.value.to_bytes()


class AnyBytes(AMQPType):
    """
    Accepts as value any sequence of bytes provided.
    """
    value: bytes
    python_cls = bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        return cls(data)

    def to_bytes(self) -> bytes:
        return self.value


class Octet(AMQPType):
    value: int
    bytes_size: int = 1
    structChar: str = 'B'
    python_cls = int

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        val, remaining = struct.unpack(
            f">{cls.structChar}", data[:cls.bytes_size]
        )[0], data[cls.bytes_size:]
        return cls(val), remaining

    def to_bytes(self) -> bytes:
        return struct.pack(
            f'>{self.structChar}', self.python_cls(self.value)
        )


@amqp_fields
class Boolean(Octet):
    structChar = '?'
    type_str = 't'
    python_cls = bool


@amqp_fields
class ShortShortInt(Octet):
    structChar = 'b'
    type_str = 'b'
    python_cls = int


@amqp_fields
class ShortShortUint(Octet):
    structChar = 'B'
    type_str = 'B'
    python_cls = int


@amqp_fields
class ShortInt(Octet):
    structChar = 'h'
    type_str = 'U'
    bytes_size = 2
    python_cls = int


@amqp_fields
class ShortSignedInt(ShortInt):
    type_str = 's' # https://www.rabbitmq.com/amqp-0-9-1-errata.html#section_3


@amqp_fields
class ShortUint(Octet):
    structChar = 'H'
    type_str = 'u'
    bytes_size = 2
    python_cls = int


@amqp_fields
class LongInt(Octet):
    structChar = 'l'
    type_str = 'I'
    bytes_size = 4
    python_cls = int


@amqp_fields
class LongUint(Octet):
    structChar = 'L'
    type_str = 'i'
    bytes_size = 4
    python_cls = int


@amqp_fields
class LongLongInt(Octet):
    structChar = 'q'
    type_str = 'L'
    bytes_size = 8
    python_cls = int


@amqp_fields
class LongLongUint(Octet):
    structChar = 'Q'
    type_str = 'l'
    bytes_size = 8
    python_cls = int


@amqp_fields
class Float(Octet):
    structChar = 'f'
    type_str = 'f'
    bytes_size = 4
    python_cls = float


@amqp_fields
class Double(Octet):
    structChar = 'd'
    type_str = 'd'
    bytes_size = 8
    python_cls = float


@amqp_fields
class DecimalValue(AMQPType):
    # Format modified from RabbitMQ errata
    # https://www.rabbitmq.com/amqp-0-9-1-errata.html#section_3

    value: Decimal
    type_str = 'D'
    python_cls = Decimal

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        scale, remaining = Octet.from_bytes(data)
        value, remaining = struct.unpack(">i", remaining[:4])[0], remaining[4:]
        # long_uint, remaining = LongUint.from_bytes(remaining)
        value = Decimal(value)
        val = Decimal((0, value.as_tuple().digits, -scale.value))
        return cls(val), remaining

    def to_bytes(self) -> bytes:
        signal, digits, scale = self.value.as_tuple()
        scale = Octet(abs(scale)).to_bytes()
        digits = ''.join(map(str, digits))
        value = struct.pack(">i", int(digits))
        return scale + value


@amqp_fields
class ShortString(AMQPType):
    value: str
    type_str = None # https://www.rabbitmq.com/amqp-0-9-1-errata.html#section_3
    python_cls = str

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        size, remaining = struct.unpack(">B", data[:1])[0], data[1:]

        value, remaining = struct.unpack(
            f">{size}s", remaining[:size]
        )[0], remaining[size:]

        return cls(value.decode()), remaining

    def to_bytes(self) -> bytes:
        data = self.value.encode()
        return Octet(len(data)).to_bytes() + data


@amqp_fields
class LongString(AMQPType):
    value: str
    type_str = 'S'
    python_cls = str

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        size, remaining = LongUint.from_bytes(data)
        value = struct.unpack(
            f">{size.value}s", remaining[:size.value]
        )[0]
        return cls(value.decode()), remaining[size.value:]

    def to_bytes(self) -> bytes:
        data = self.value.encode()
        return LongUint(len(data)).to_bytes() + data


@amqp_fields
class FieldArray(AMQPType):
    # Change from RabbitMQ where it considers the size as long-uint instead
    # of long-int.
    # https://www.rabbitmq.com/amqp-0-9-1-errata.html#section_4
    value: List[FieldValue]
    type_str = 'A'
    python_cls = list

    def __init__(self, value: List[AMQPType] = None):
        if value is not None:
            values_list = [
                v if isinstance(v, FieldValue) else FieldValue(v)
                for v in value
            ]
            super(FieldArray, self).__init__(values_list)
        else:
            super(FieldArray, self).__init__(value)            

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        size, remaining = LongUint.from_bytes(data)
        value_array = remaining[:size.value]
        values = []
        while value_array:
            val, value_array = FieldValue.from_bytes(value_array)
            values.append(val)
        return values, remaining[size.value:]

    def to_bytes(self) -> bytes:
        data = b''
        for v in self.value:
            data += v.to_bytes()
        return LongInt(len(data)).to_bytes() + data

    def to_python(self):
        return [
            v.to_python() if isinstance(v, AMQPType) else v
            for v in self.value
        ]


class FieldValuePair(AMQPType):
    value = Tuple[ShortString, FieldValue]
    python_cls = tuple

    def __init__(self, field_name=None, field_value: AMQPType=None):
        if field_name is not None and field_value is not None:
            if not isinstance(field_name, ShortString):
                field_name = ShortString(field_name)
    
            if not isinstance(field_value, FieldValue):
                field_value = FieldValue(field_value)
    
            super(FieldValuePair, self).__init__((field_name, field_value))
        else:
            super(FieldValuePair, self).__init__(None)

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        field_name, remaining = ShortString.from_bytes(data)
        field_value, remaining = FieldValue.from_bytes(remaining)
        return cls(field_name, field_value), remaining

    def to_bytes(self) -> bytes:
        return self.value[0].to_bytes() + self.value[1].to_bytes()

    def to_python(self):
        return (
            self.value[0].to_python() if isinstance(self.value[0], AMQPType)
            else self.value[0],
            self.value[1].to_python() if isinstance(self.value[1], AMQPType)
            else self.value[1]
        )


@amqp_fields
class FieldTable(AMQPType):
    value: Dict[str, FieldValue]
    type_str = 'F'
    python_cls = dict

    @classmethod
    def _get_table(cls, data: bytes) -> Dict[str, Any]:
        fields = {}
        field_value_pairs = data
        while field_value_pairs:
            field, field_value_pairs = FieldValuePair.from_bytes(
                field_value_pairs
            )
            fields[field.value[0].value] = field.value[1].value
        return fields

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        size, remaining = LongUint.from_bytes(data)
        table = cls._get_table(remaining[:size.value])
        return cls(table), remaining[size.value:]

    def to_bytes(self) -> bytes:
        data = b''
        for name, value in self.value.items():
            data += FieldValuePair(name, value).to_bytes()
        size = LongUint(len(data)).to_bytes()
        return size + data

    def to_python(self):
        return {
            name: value.to_python() if isinstance(value, AMQPType) else value
            for name, value in self.value.items()
        }


@amqp_fields
class NoField(AMQPType):
    value = None
    type_str = 'V'
    python_cls = lambda x: None

    def __init__(self):
        super(NoField, self).__init__()

    def to_bytes(self) -> bytes:
        return b''

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        return cls(), data


@amqp_fields
class Timestamp(AMQPType):
    value: datetime
    type_str = 'T'
    python_cls = datetime.now

    def __init__(self, value: Union[datetime, int] = None):
        if value is not None and isinstance(value, int):
            value = datetime.fromtimestamp(value)
        super(Timestamp, self).__init__(value)

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["AMQPType", bytes]:
        posix_time, remaining = LongLongUint.from_bytes(data)
        return cls(posix_time.value), remaining

    def to_bytes(self) -> bytes:
        return LongLongUint(self.value.timestamp()).to_bytes()
