class AMQPException(Exception):
    ...

class ProtocolError(AMQPException):
    ...

class WrongType(ProtocolError):
    ...

class FrameEndError(ProtocolError):
    ...

class AMQPReplyError(ProtocolError):
    ...


class ContentTooLarge(AMQPReplyError):
    value = 311

class NoConsumers(AMQPReplyError):
    value = 313

class ConnectionForced(AMQPReplyError):
    value = 320

class InvalidPath(AMQPReplyError):
    value = 402

class AccessRefused(AMQPReplyError):
    value = 403

class NotFound(AMQPReplyError):
    value = 404

class ResourceLocked(AMQPReplyError):
    value = 405

class PreconditionFailed(AMQPReplyError):
    value = 406

class FrameError(AMQPReplyError):
    value = 501

class SyntaxError(AMQPReplyError):
    value = 502

class CommandInvalid(AMQPReplyError):
    value = 503

class ChannelError(AMQPReplyError):
    value = 504

class UnexpectedFrame(AMQPReplyError):
    value = 505

class ResourceError(AMQPReplyError):
    value = 506

class NotAllowed(AMQPReplyError):
    value = 530

class NotImplemented(AMQPReplyError):
    value = 540

class InternalError(AMQPReplyError):
    value = 541

reply_exceptions = {
    311: ContentTooLarge,
    313: NoConsumers,
    320: ConnectionForced,
    402: InvalidPath,
    403: AccessRefused,
    404: NotFound,
    405: ResourceLocked,
    406: PreconditionFailed,
    501: FrameError,
    502: SyntaxError,
    503: CommandInvalid,
    504: ChannelError,
    505: UnexpectedFrame,
    506: ResourceError,
    530: NotAllowed,
    540: NotImplemented,
    541: InternalError
}

def raise_error_from_server(reply_code, reply_text):
    exc = reply_exceptions[reply_code]
    raise exc(reply_text)
