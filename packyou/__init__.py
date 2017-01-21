import sys
import logging

import requests
import requests_cache

requests_cache.install_cache('packyou_cache')


def init_logging(level=None):
    logger = logging.getLogger('packyou')
    if not level:
        logger.setLevel(logging.INFO)
    if level == 'warning':
        logger.setLevel(logging.WARN)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('packyou.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.warning('Logging level set to {0}'.format(level))

if (sys.version_info > (3, 0)):
    # Python 3
    from packyou import py3
else:
    # Python 2
    from packyou import py2


init_logging()
