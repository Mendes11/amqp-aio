# from typing import Tuple
#
#
# from .conts import METHOD_TYPE, HEADER_TYPE, BODY_TYPE, HEARTBEAT_TYPE
# from .frames import Frame, ContentHeaderFrame, ContentBodyFrame, \
#     HeartBeatFrame, MethodFrame
#
#
# def parse_frame(data: bytes) -> Tuple[Frame, bytes]:
#     """
#     Parses the bytes data returning the appropriate Frame based on it
#     :param data: Received Data from the other peer
#     :return: Frame, Remaining Bytes
#     """
#     f, _ = Frame.from_bytes(data)
#
#     if f.frame_type == METHOD_TYPE:
#         return MethodFrame.from_bytes(data)
#
#     elif f.frame_type == HEADER_TYPE:
#         return ContentHeaderFrame.from_bytes(data)
#
#     elif f.frame_type == BODY_TYPE:
#         return ContentBodyFrame.from_bytes(data)
#
#     elif f.frame_type == HEARTBEAT_TYPE:
#         return HeartBeatFrame.from_bytes(data)
#
#     raise