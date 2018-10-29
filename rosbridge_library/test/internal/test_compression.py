#!/usr/bin/env python
import sys
import rospy
import rostest
import unittest

from rosbridge_library.internal import cbor, pngcompression

PYTHON2 = sys.version_info < (3, 0)


class TestCompression(unittest.TestCase):

    def setUp(self):
        rospy.init_node("test_compression")

    def test_compress_png(self):
        bytes = list(range(128)) * 10000
        string = str(bytearray(bytes))
        encoded = pngcompression.encode(string)
        self.assertNotEqual(string, encoded)

    def test_compress_decompress_png(self):
        bytes = list(range(128)) * 10000
        string = str(bytearray(bytes))
        encoded = pngcompression.encode(string)
        self.assertNotEqual(string, encoded)
        decoded = pngcompression.decode(encoded)
        self.assertEqual(string, decoded)

    def test_compress_decompress_cbor(self):
        msg = {"foo": "bar", "data": bytes(list(range(128)) * 10000)}
        encoded = cbor.encode(msg)
        # must encode to b64 str/bytes
        if PYTHON2:
            self.assertTrue(isinstance(encoded, str))
        else:
            self.assertTrue(isinstance(encoded, bytes))
        decoded = cbor.decode(encoded)
        self.assertEqual(msg, decoded)

PKG = 'rosbridge_library'
NAME = 'test_compression'
if __name__ == '__main__':
    rostest.unitrun(PKG, NAME, TestCompression)

