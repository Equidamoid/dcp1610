import easysnmp
import zeroconf
import logging
import time

logger = logging.getLogger(__name__)


class ScannerFinder:
    svc_type = "_scanner._tcp.local."

    def __init__(self):
        pass
        logger.info("Querying MDNS for %s", self.svc_type)
        self._address = None

    def add_service(self, zc, type_, name):
        if self._address:
            logger.warning("Got second response, scanner selection is not implemented, so ignoring it.")
        logger.error("Got service: %s %s", type_, name)
        data = zc.get_service_info(type_, name)
        addr = '.'.join([str(i) for i in data.address])
        mfg = data.properties.get(b'mfg', '[NO_DATA]')
        model = data.properties.get(b'mdl', '[NO_DATA]')
        button = data.properties.get(b'button', None) == b'T'
        flatbed = data.properties.get(b'flatbed', None) == b'T'
        feeder = data.properties.get(b'feeder', None) == b'T'
        logger.warning("Scanner found: addr=%s:%d, mfg=%s, model=%s, buttons=%s, feeder=%s, flatbed=%s",
                       addr, data.port, mfg, model, button, feeder, flatbed)
        self._address = addr
        self._model = model
        self._port = data.port

    def query(self):
        self.zc = zeroconf.Zeroconf()
        self.br = zeroconf.ServiceBrowser(self.zc, self.svc_type, self)
        for i in range(50):
            if self._address:
                self.br.cancel()
                return self._address, self._model
            time.sleep(0.1)
        logger.error("No scanner found in 5 sec")


def find_scanner():
    f = ScannerFinder()
    return f.query()
