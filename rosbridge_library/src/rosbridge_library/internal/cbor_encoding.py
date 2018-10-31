import struct
import traceback

from rosbridge_library.internal.cbor_lib import dumps, loads, Tag
from genpy.message import Message


ARRAY_TYPES = {
    'int8[]': (72, '{}b'),
    'int16[]': (73, '<{}h'),
    'int32[]': (74, '<{}i'),
    'int64[]': (75, '<{}l'),
    'uint16[]': (65, '<{}H'),
    'uint32[]': (66, '<{}I'),
    'uint64[]': (67, '<{}L'),
    'float16[]': (81, '{}f'),
    'float32[]': (81, '{}f'),
    'float64[]': (82, '{}d'),
}


def _is_ros_msg(o):
    return isinstance(o, Message)


def _msg_to_dict(msg):
    out = {}
    for slot, slot_type in zip(msg.__slots__, msg._slot_types):
        val = getattr(msg, slot)

        # nested message
        if _is_ros_msg(val):
            out[slot] = _msg_to_dict(val)

        # string
        elif slot_type == 'string':
            out[slot] = str(val)

        # byte array
        elif slot_type == 'uint8[]':
            out[slot] = bytearray(val)

        # bool
        elif slot_type == 'bool':
            out[slot] = bool(val)

        # integers
        elif slot_type in ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']:
            out[slot] = int(val)

        # floats
        elif slot_type in ['float32', 'float64']:
            out[slot] = float(val)

        # integer arrays
        elif slot_type in ARRAY_TYPES:
            tag, fmt = ARRAY_TYPES[slot_type]
            packed = bytearray(struct.pack(fmt.format(len(val)), *val))
            out[slot] = Tag(tag=tag, value=packed)

        # time/duration
        elif slot_type in ['time', 'duration']:
            out[slot] = {
                'secs': int(val.secs),
                'nsecs': int(val.nsecs),
            }

        # any other iterable
        elif hasattr(val, '__iter__'):
            if len(val) == 0:
                out[slot] = []
            elif _is_ros_msg(val[0]):
                out[slot] = [_msg_to_dict(i) for i in val]
            else:
                out[slot] = val[:]

        # anything else?
        else:
            out[slot] = val

    return out


def encode(msg):
    try:
        msg = msg.copy()
        for k, v in msg.items():
            if _is_ros_msg(v):
                msg[k] = _msg_to_dict(v)

        buf = bytearray(dumps(msg))
    except:
        traceback.print_exc()
        raise
    return buf


def decode(msg):
    return loads(msg)
