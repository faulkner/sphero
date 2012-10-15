import unittest2
from sphero import request
from nose.tools import assert_equal


class RequestTest(unittest2.TestCase):
    def test_ping(self):
        assert_equal('\xff\xff\x00\x01\x00\x01\xfd', request.Ping().bytes)

    def test_set_rgb(self):
        response = request.SetRGB(0, 0, 100, 200, 0)
        assert_equal('\x00d\xC8\x00', response.packet_body())
