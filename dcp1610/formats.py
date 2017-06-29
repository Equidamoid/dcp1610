import logging
import PIL.Image

logger = logging.getLogger(__name__)


class PilBuffer(object):
    def get_image(self):
        raise NotImplementedError()

    def save(self, filename):
        self.get_image().save(filename)


class GrayscaleBuffer(PilBuffer):
    def __init__(self, w, h):
        self.buf = b''
        self.w = w
        self.h = h
        self.estimated_len = w * h

    def handle_line(self, t, data):
        assert t == 0x40
        self.buf += data

    def get_image(self):
        return PIL.Image.frombuffer('L', (self.w, self.h), self.buf, 'raw', 'L', 0, 1)

    def get_progress(self):
        return len(self.buf) / self.estimated_len


class YcbcrBuffer(PilBuffer):
    def __init__(self, w, h):
        self.r = b''
        self.g = b''
        self.b = b''
        self.w = w
        self.h = h
        self.estimated_len = w * h

    def handle_line(self, t, data):
        if t == 0x44:
            self.r += data
        if t == 0x48:
            self.g += data
        if t == 0x4c:
            self.b += data

    def get_image(self):
        logger.debug('YCC buffers: %5d %5d %5d', len(self.r), len(self.g), len(self.b))
        r = PIL.Image.frombuffer('L', (self.w, self.h), self.r, 'raw', 'L', 0, 1)
        g = PIL.Image.frombuffer('L', (self.w, self.h), self.g, 'raw', 'L', 0, 1)
        b = PIL.Image.frombuffer('L', (self.w, self.h), self.b, 'raw', 'L', 0, 1)
        return PIL.Image.merge('YCbCr', [g, b, r]).convert('RGB')

    def get_progress(self):
        return len(self.b) / self.estimated_len
