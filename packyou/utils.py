import os
import logging
from functools import lru_cache

from tqdm import tqdm
from git import RemoteProgress

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))
LOGGER = logging.getLogger(__name__)


class TQDMCloneProgress(RemoteProgress):

    def __init__(self):
        super().__init__()
        self.progress = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        if not self.progress:
            self.progress = tqdm(total=max_count)
        self.progress.update(n=cur_count)


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper
