import logging
import binascii
import socket
import struct
import time
from .formats import GrayscaleBuffer, YcbcrBuffer

logger = logging.getLogger(__name__)

MODE_CGRAY = 'CGRAY'
MODE_GRAY64 = 'GRAY64'

do_optional_handshake = True


def scale_size(v, limit):
    if v <= 1:
        v = v * limit

    return int(v)


def recv_all(s, l):
    buf = b''
    while len(buf) < l:
        tbuf = s.recv(l - len(buf))
        if not tbuf:
            raise RuntimeError("can't recv()")
        buf += tbuf
    return buf


def get_chunk(s: socket.socket):
    pl_type = recv_all(s, 2)[0]
    logger.debug("Packet type: %x", pl_type)
    if pl_type == 0x82:
        logger.info("Stop packet received")
        return pl_type, None

    hdr = recv_all(s, 10)

    fields = struct.unpack('hhhhh', hdr)
    pl_len = fields[-1]
    logger.debug("Header: %s, payload len: %d", binascii.hexlify(hdr), pl_len)
    return pl_type, recv_all(s, pl_len)


def wrap_request(t, fields):
    if isinstance(fields, list):
        fields = ''.join(['%s=%s\n' % k for k in fields])
    return b'\x1b%s\n%s\x80' % (t, fields.encode())



class ScanTask(object):
    def __init__(self, addr, w=1.0, h=1.0, x=0, y=0, res=100, mode=MODE_GRAY64):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.sock = None
        self.addr = addr
        self.res = res
        self.mode = mode

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.addr, 54921))

        hello = self.sock.recv(64)
        logger.info("Hello from printer: %r", hello)

        if b'NG 401' in hello:
            logger.error("Got error from scanner. Is it in use by another client?")

        if do_optional_handshake:
            logger.warning("Performing handshake")

            # 'Q'
            self.sock.send(binascii.unhexlify('1b510080'))
            tmp = self.sock.recv(128)
            logger.info("Q: %s", binascii.hexlify(tmp))

            # "Document feeder present?"
            self.sock.send(wrap_request(b'D', 'ADF\n'))
            tmp = self.sock.recv(32)
            logger.info("ADF: %s", binascii.hexlify(tmp))
            assert tmp == b'\xd0'

            # "Flatbed?"
            self.sock.send(wrap_request(b'D', 'FB\n'))
            tmp = self.sock.recv(32)
            logger.info("FB: %s", binascii.hexlify(tmp))
            assert tmp == b'\x80'

    def make_req1(self):
        params = [
            ('R', '%d,%d' % (self.res, self.res)),
            ('M', self.mode),
            ('D', 'SIN'),
            ('S', 'NORMAL_SCAN'),
        ]
        return wrap_request(b'I', params)

    def make_req2(self):
        params = [
            ('R', '%d,%d' % (self.res, self.res)),
            ('M', self.mode),
            ('B', 50),
            ('N', 50),
            ('C', 'NONE'),  # compression, 'J=MID'
            ('A', '%d,%d,%d,%d' % (self.x, self.y, self.w + self.x, self.h + self.y)),
            ('S', 'NORMAL_SCAN'),
            ('P', 0),
            ('E', 0),
            ('G', 0),
        ]
        return wrap_request(b'X', params)

    def read_dimensions(self):
        self.sock.send(self.make_req1())
        resp = self.sock.recv(80)
        logger.info("Dimensions response: %r", resp)
        resp = resp[3:]
        fields = str(resp.decode()).split(',')
        resx, resy = int(fields[0]), int(fields[1])
        dx, dy = int(fields[3]), int(fields[5])
        mw, mh = int(fields[4]), int(fields[6])
        if self.res != resx or self.res != resy:
            minres = min(resx, resy)
            logger.warning("Scanner reported use of resolution [%d %d] instead of %d, changing resolution to %d",
                           resx, resy, self.res, minres)
            self.res = minres
        logger.warning("Page size: %dx%d (%dx%d mm)", mw, mh, dx, dy)

        self.x = scale_size(self.x, mw)
        self.y = scale_size(self.y, mh)
        self.w = scale_size(self.w, mw)
        self.h = scale_size(self.h, mh)

        self.w = min(self.w, mw - self.x)
        self.h = min(self.h, mh - self.y)

        logger.info("Image dimensions: %d x %d, origin: %d, %d", self.w, self.h, self.x, self.y)

    def do_scan(self, filename):
        self.connect()
        self.read_dimensions()
        if self.mode == MODE_GRAY64:
            buffer = GrayscaleBuffer(self.w, self.h)
        elif self.mode == MODE_CGRAY:
            buffer = YcbcrBuffer(self.w, self.h)

        logger.warning('Scanning image, size: %dx%d, mode=%s', self.w, self.h, self.mode)
        self.sock.send(self.make_req2())

        last_progress_mark = -1
        start = None
        while True:
            t, data = get_chunk(self.sock)
            if (t & 0x40) != 0x40:
                break
            buffer.handle_line(t, data)
            if start is None:
                start = time.time()
            progress = buffer.get_progress()
            progress_mark = int(progress * 20)  # 5% step
            if progress_mark != last_progress_mark:
                if progress > 0.04:
                    eta = (time.time() - start) * (1 / progress - 1)
                    logger.info("Receiving data, %d%% done, ~%d sec remaining", progress * 100, eta)
                last_progress_mark = progress_mark

        logger.info("Writing output")
        buffer.save(filename)

        self.sock.close()
