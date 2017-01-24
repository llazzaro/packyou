from os import walk
from os.path import (
    abspath,
    join,
    dirname,
    split,
    isdir
)
import sys
import logging

import requests_cache

# requests_cache.install_cache('packyou_cache')
MODULES_PATH = dirname(abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = join(MODULES_PATH, 'github')


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


def find_module_path_in_cloned_repos(fullname):
    splitted_fullname = fullname.split('.')
    for root, subdirs, files in walk(MODULES_PATH):
        current_dir = split(root)[-1]
        parent, _, current_dir = root.rpartition('/')
        if isdir(root):
            if splitted_fullname[0] == current_dir:
                splitted_fullname.pop(0)

        if len(splitted_fullname) == 1:
            for filename in files:
                if '{0}.py'.format(splitted_fullname[0]) == filename:
                    return [parent]

        if not splitted_fullname:
            # check if the module is here
            return [parent]


def find_module_in_cloned_repos(fullname, loader_class):
    path = find_module_path_in_cloned_repos(fullname)
    loader = loader_class(fullname, path)
    return loader.load_module(fullname)

if (sys.version_info > (3, 0)):
    # Python 3
    from packyou import py3
else:
    # Python 2
    from packyou import py2


init_logging()
