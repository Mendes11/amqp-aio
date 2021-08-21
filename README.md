# AMQP-AIO

Library Implementing the AMQP Protocol, with RabbitMQ extension.



>Note: This library is incomplete, do not use it!


### AMQP Frames

This library implements all AMQP frames as classes in `amqp` package, so you 
can use it to create your own client library.

To use the frames, simply:

```python
from amqp_aio.amqp.frames import Frame
from amqp_aio.amqp.connection import Open

channel = 0
received_data = b'peer data in here'

parsed_frame = Frame.from_bytes(received_data)
print(parsed_frame)

to_send_frame = Frame.from_frame(
    Open(
        virtual_host='/'
    ), channel=channel
).to_bytes()
print(to_send_frame)
```


### AMQP Client

> Work in Progress.\
> Currently the client can only perform the full connection procedure (with 
> PLAIN authentication) and 
> exchange heartbeats with the other peer.

