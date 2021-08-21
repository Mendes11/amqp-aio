import inspect

from amqp_aio.amqp.consts import METHOD_TYPE, HEARTBEAT_TYPE
from amqp_aio.amqp.frames import Frame, MethodArguments, HeartbeatFrame


class FrameRouter:
    """
    Routes an incoming Frame to it's respective method
    """

    def __init__(self):
        self._method_routes = {}
        self._heartbeat_route = None

    def _validate_route(self, route):
        params = inspect.signature(route).parameters
        if len(params) != 1:
            raise ValueError(
                "Route {} must have 1 argument (frame)".format(route)
            )

    def register_route(self, channel, frame, route):
        self._validate_route(route)
        if issubclass(frame, MethodArguments):
            self._method_routes.setdefault(channel, {})[frame] = route
        elif issubclass(frame, HeartbeatFrame):
            self._heartbeat_route = route
        else:
            raise TypeError(
                "This router is unable to route {} frame".format(frame)
            )

    async def route_frame(self, frame: Frame):
        if frame.frame_type == METHOD_TYPE: # Method Frame
            route = self._method_routes[frame.channel][type(
                frame.payload.arguments)]
            await route(frame.payload.arguments)
        if frame.frame_type == HEARTBEAT_TYPE:
            route = self._heartbeat_route
            await route(frame)
