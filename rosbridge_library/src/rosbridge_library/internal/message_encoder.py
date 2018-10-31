from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import threading

from rosbridge_library.internal.pngcompression import encode as encode_png
from rosbridge_library.internal.cbor_encoding import encode as encode_cbor
from rosbridge_library.internal.message_conversion import extract_values

try:
    from ujson import dumps as encode_json
except ImportError:
    try:
        from simplejson import dumps as encode_json
    except ImportError:
        from json import dumps as encode_json


class OutgoingMessageEncoder(object):
    def __init__(self, message):
        self.message = message

        self._cache_lock = threading.Lock()
        self._cache = {}

    def get_publish(self, topic, compression):
        with self._cache_lock:
            if not compression in self._cache:
                self._cache[compression] = {
                    "lock": threading.Lock(),
                    "encoded": None,
                }

        cache = self._cache[compression]
        with self._cache[compression]["lock"]:
            if cache["encoded"] is None:
                cache["encoded"] = self._encode_publish(topic, compression)

        return cache["encoded"]

    def _encode_publish(self, topic, compression):
        payload = {"op": "publish", "topic": topic}

        message = self.message

        if compression == "none":
            payload["msg"] = extract_values(message)
            return encode_json(payload)

        if compression == "png":
            payload["msg"] = extract_values(message)
            json = encode_json(payload)
            wrapper = {"op": "png", "data": encode_png(json)}
            return encode_json(wrapper)

        if compression == "cbor":
            payload["msg"] = message
            return encode_cbor(payload)

        raise Exception("Unknown compression type: {}".format(compression))
