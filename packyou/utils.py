import os
import ipdb
import logging
from os.path import isdir, join, dirname, abspath, exists

from tqdm import tqdm
from git import RemoteProgress

MODULES_PATH = dirname(abspath(__file__))
LOGGER = logging.getLogger(__name__)

class TQDMCloneProgress(RemoteProgress):

    def __init__(self):
        super(TQDMCloneProgress, self).__init__(self)
        self.progress = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        pdb.set_trace()
        if not self.progress:
            self.progress = tqdm(total=max_count)
        update(n=cur_count)


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
