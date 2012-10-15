import serial
import struct
import logging
import glob

import request


class SpheroError(Exception):
    pass


class Sphero(object):
    def __init__(self, path=None):
        self.sp = None
        self.dev = 0x00
        self.seq = 0x00
        self.set_sphero(path)

    def set_sphero(self, path=None):
        if not path:
            spheros = self.paired_spheros()
            if not spheros:
                raise SpheroError('you need to pair with a Sphero first')
            path = spheros[-1]

        self.path = path

    def paired_spheros(self):
        return glob.glob('/dev/tty.Sphero*')

    def connect(self, retry=100):
        logging.info('connecting to %s' % self.path)
        while True:
            try:
                self.sp = serial.Serial(self.path, 115200)
                return
            except serial.serialutil.SerialException:
                logging.info('retrying')
                if not retry:
                    raise SpheroError('failed to connect after %d tries' % retry)
                retry -= 1

    def write(self, packet):
        self.sp.write(str(packet))
        self.seq += 1
        if self.seq == 0xFF:
            self.seq = 0x00

        header = struct.unpack('5B', self.sp.read(5))
        body = self.sp.read(header[-1])

        response = packet.response(header, body)

        if response.success:
            return response
        else:
            raise SpheroError('request failed (request: %s:%s, response: %s:%s)' % (header, repr(body), response.header, repr(response.body)))

    def ping(self):
        return self.write(request.Ping(self.seq))

    def set_rgb(self, r, g, b, persistant=False):
        return self.write(request.SetRGB(self.seq, r, g, b, 0x01 if persistant else 0x00))

    def get_rgb(self):
        return self.write(request.GetRGB(self.seq))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    s = Sphero()
    s.connect()

    # connected?  throw a rave!
    import random
    for x in range(100):
        s.set_rgb(random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255))
