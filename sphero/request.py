import struct
import response


class Request(object):
    SOP1 = 0xFF
    SOP2 = 0xFF
    did = 0x00
    cid = 0x00

    def __init__(self, seq=0x00, *data):
        self.seq = seq
        self.data = data

    def __str__(self):
        return self.bytes

    @property
    def fmt(self):
        return '%sB' % len(self.data)

    def checksum(self):
        body = self.packet_header() + self.packet_body()
        body = struct.unpack('%sB' % len(body), body)
        return struct.pack('B', ~(sum(body[2:]) % 256) & 0xFF)

    @property
    def bytes(self):
        return self.packet_header() + self.packet_body() + self.checksum()

    def packet_header(self):
        return struct.pack('6B', *self.header())

    def packet_body(self):
        if not self.data:
            return ''

        return struct.pack(self.fmt, *self.data)

    @property
    def dlen(self):
        return struct.calcsize(self.fmt) + 1

    def header(self):
        return [self.SOP1, self.SOP2, self.did, self.cid, self.seq, self.dlen]

    def response(self, header, body):
        name = self.__class__.__name__.split('.')[-1]
        klass = getattr(response, name, response.Response)
        return klass(header, body)


class Core(Request):
    did = 0x00

class Ping(Core):
    cid = 0x01


class Sphero(Request):
    did = 0x02

class SetRGB(Sphero):
    cid = 0x20

class GetRGB(Sphero):
    cid = 0x22
