import sys
import logging
from pathlib import Path

MODULES_PATH = str(Path(__file__).parent)
GITHUB_REPOSITORIES_DIRECTORY = str(Path(MODULES_PATH) / 'github')
LOGGER = logging.getLogger(__name__)


def init_logging(level=None):
    logger = logging.getLogger('packyou')
    if not level:
        logger.setLevel(logging.INFO)
    if level == 'warning':
        logger.setLevel(logging.WARN)
    fh = logging.FileHandler('packyou.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.warning(f'Logging level set to {level}')


def get_root_path():
    return str(Path(__file__).parent)


def find_module_path_in_cloned_repos(fullname):
    splitted_fullname = fullname.split('.')
    for root, subdirs, files in Path(MODULES_PATH).walk():
        root_str = str(root)
        current_dir = root.name
        if root.is_dir():
            if splitted_fullname[0] == current_dir:
                splitted_fullname.pop(0)
                LOGGER.info(f'POP -> {splitted_fullname}')

        if len(splitted_fullname) == 1:
            for filename in files:
                if f'{splitted_fullname[0]}.py' == filename:
                    LOGGER.info(f'found -> {filename}')
                    LOGGER.info(f'root -> {root_str}')
                    return [root_str], None

        if not splitted_fullname:
            return [root_str], None

    remaining = '.'.join(splitted_fullname)
    return [], remaining


from packyou import py3  # noqa: E402, F401
