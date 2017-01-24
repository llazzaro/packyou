import sys
import logging
from os import walk
from os.path import (
    abspath,
    join,
    dirname,
    split,
    isdir
)

import requests_cache

# requests_cache.install_cache('packyou_cache')
MODULES_PATH = dirname(abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = join(MODULES_PATH, 'github')
LOGGER = logging.getLogger(__name__)


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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.warning('Logging level set to {0}'.format(level))


def get_root_path():
    return dirname(abspath(__file__))


def find_module_path_in_cloned_repos(fullname):
    splitted_fullname = fullname.split('.')
    for root, subdirs, files in walk(MODULES_PATH):
        current_dir = split(root)[-1]
        parent, _, current_dir = root.rpartition('/')
        if isdir(root):
            if splitted_fullname[0] == current_dir:
                splitted_fullname.pop(0)
                LOGGER.info('POP -> {0}'.format(splitted_fullname))

        if len(splitted_fullname) == 1:
            for filename in files:
                if '{0}.py'.format(splitted_fullname[0]) == filename:
                    LOGGER.info('found -> {0}'.format(filename))
                    LOGGER.info('root -> {0}'.format(root))
                    return [root], None

        if not splitted_fullname:
            # check if the module is here
            return [root], None

    remaining = '.'.join(splitted_fullname)
    return [], remaining


if (sys.version_info > (3, 0)):
    # Python 3
    from packyou import py3
else:
    # Python 2
    from packyou import py2


init_logging()
