import zeroconf
import logging

logger = logging.getLogger(__name__)


def find_scanner():
    logging.info("Sending zeroconf query")
    zc = zeroconf.Zeroconf()
    name = "Brother DCP-1610W series._scanner._tcp.local."
    data = zc.get_service_info('SRV' + zeroconf.service_type_name(name), name)
    addr = '.'.join([str(i) for i in data.address])
    model = data.properties.get(b'mdl', '[NO_DATA]')
    button = data.properties.get(b'button', None) == b'T'
    flatbed = data.properties.get(b'flatbed', None) == b'T'
    feeder = data.properties.get(b'feeder', None) == b'T'
    logger.warning("Scanner detected: addr=%s, model=%s, buttons=%s, feeder=%s, flatbed=%s",
                   addr, model, button, feeder, flatbed)

    return addr, model


