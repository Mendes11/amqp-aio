import inspect
from typing import Tuple, Any, Callable, Type

from amqp_aio.amqp.amqp_types import Octet, AMQPType, ShortInt, LongInt


class FrameField:
    amqp_type: Type[AMQPType] = Octet
    _params = None

    def __new__(cls, *args, **kwargs):
        instance = super(FrameField, cls).__new__(cls)
        instance._params = (args, kwargs)
        return instance

    def __init__(self, amqp_type=None, default=None):
        self.amqp_type = amqp_type or self.amqp_type
        self.parent = None
        self.field_name = None
        self.default = default

    def validate(self, value, previous: bytes) -> Any:
        if value is None:
            raise ValueError(
                f"Unable to serialize {self.field_name}. It cannot be None"
            )
        return value

    def to_bytes(self, value, previous=b'') -> bytes:
        return self.amqp_type(value).to_bytes()

    def parse_bytes(self, data: bytes) -> Tuple[Any, bytes]:
        self.amqp_value, remaining = self.amqp_type.from_bytes(data)
        return self.amqp_value.to_python(), remaining

    def bind(self, parent, field_name):
        inst = type(self)(*self._params[0], **self._params[1])
        inst.parent = parent
        inst.field_name = field_name
        return inst


class FrameSelectorField(FrameField):
    def __init__(
            self, selector: Callable[['BaseFrame'], 'BaseFrame'], **kwargs
    ):
        self.selector = selector
        super(FrameSelectorField, self).__init__(**kwargs)

    def parse_bytes(self, data: bytes) -> Tuple['BaseFrame', bytes]:
        selected_frame = self.selector(self.parent)
        frame, remaining = selected_frame.from_bytes(data)
        return frame, remaining

    def to_bytes(self, value, previous=b'') -> bytes:
        if not isinstance(value, BaseFrame):
            raise TypeError(f'{value} is not a subclass of BaseFrame')
        return value.to_bytes()


class FrameMetadata:
    parsing_order = []
    original_fields = {}

    def __init__(self, meta, _class):
        self.parsing_order = getattr(meta, 'parsing_order', [])
        self.original_fields = {}
        self.meta = meta


class FrameCreator(type):
    def __new__(cls, name, bases, attrs):
        _class = super(FrameCreator, cls).__new__(cls, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, FrameCreator)]
        if not parents:
            return super(FrameCreator, cls).__new__(cls, name, bases, attrs)

        # If the class has a parent, it will already have a _meta attribute
        base_meta = getattr(_class, '_meta', None)

        # And if a new one was given, we load it
        _meta = attrs.pop('Meta', None) or getattr(_class, 'Meta', None)

        fields = (getattr(base_meta, 'original_fields') if base_meta else {

        }).copy()
        fields.update({
            field_name: value
            for field_name, value in inspect.getmembers(
                _class, lambda x: isinstance(x, FrameField)
            )
        })

        if _meta is None:
            class Meta:
                parsing_order = fields.keys()
            _meta = Meta

        meta = FrameMetadata(_meta, _class)
        setattr(_class, "_meta", meta)
        setattr(meta, 'original_fields', fields)

        _fields = []
        for field_name in meta.parsing_order:
            if field_name not in fields:
                raise ValueError(
                    f'Field {field_name} is missing in {name} class')

            _fields.append((field_name, fields[field_name]))

            # Recreate the fields to have their python representation
            setattr(_class, field_name, None)
        setattr(_class, "_fields", _fields)
        return _class


class BaseFrame(metaclass=FrameCreator):
    def __init__(self, **kwargs):
        bind_fields = []
        for name, field in self._fields:
            bind = field.bind(self, name)
            setattr(self, name, kwargs.get(name, field.default))
            bind_fields.append((name, bind))
        self._fields = bind_fields

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple['BaseFrame', bytes]:
        frame = cls()
        # For each Field, we call its parse_bytes method
        for name, field in frame._fields:
            value, data = field.parse_bytes(data)
            setattr(frame, name, value)
        return frame, data

    def to_bytes(self) -> bytes:
        """
        Go the reverse order, serializing the fields one by one, from the
        latest to the earliest
        :return: Serialized Fields
        """
        data = b''
        for name, field in self._fields[::-1]:
            field_value = getattr(self, name)
            validate_fn = getattr(self, f'validate_{name}', field.validate)
            validated_value = validate_fn(field_value, data)
            fn = getattr(self, 'f{name}_to_bytes', field.to_bytes)
            serialized_field = fn(validated_value, data)
            data = serialized_field + data
        return data

    @property
    def fields(self):
        return dict(self._fields)

    def to_dict(self, recursive=True):
        d = {}
        for name in self.fields.keys():
            value = getattr(self, name)
            if recursive and hasattr(value, "to_dict"):
                value = value.to_dict()
            d[name] = value
        return d
