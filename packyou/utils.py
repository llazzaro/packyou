import os
import pdb

from tqdm import tqdm
from git import RemoteProgress

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))


class TQDMCloneProgress(RemoteProgress):

    def __init__(self):
        super(TQDMCloneProgress, self).__init__(self)
        self.progress = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        pdb.set_trace()
        if not self.progress:
            self.progress = tqdm(total=max_count)
        update(n=cur_count)


def get_filename(fullname):
    fullname_parts = fullname.split('.')[1:]
    filename = os.path.join(MODULES_PATH, '/'.join(fullname_parts))
    if os.path.isdir(filename):
        filename = os.path.join(filename, '__init__.py')
    else:
        if not filename.endswith('py'):
            filename = '{0}.py'.format(filename)
    return filename


def get_source(fullname):
    filename = get_filename(fullname)

    with open(filename, 'r') as source_file:
        return source_file.read()
