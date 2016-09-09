# -*- coding: utf-8 -*-
import os
import imp
import sys

from git import Repo

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))


class ImportFromGithub:
    """
        Import hook that will allow to import from a  github repo.
    """
    def __init__(self):
        self.path = None
        self.call_mapping = {
            1: 'github',
            2: 'username',
            3: 'repository_name',
        }

    def find_module(self, fullname, path=None):
        if fullname.startswith('packyou.github'):
            self.path = path
            return self

    def find_and_load_module(self, name, complete_name):
        if complete_name in sys.modules:
            return sys.modules[name]
        module_info = imp.find_module(name, self.path)
        module = imp.load_module(name, *module_info)
        sys.modules[complete_name] = module
        return module

    def clone_github_repo(self, username, repository_name):
        repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name)
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

    def load_module(self, name):
        complete_name = name
        splitted_names = name.split('.')
        username = None
        if len(splitted_names) >= 3:
            username = splitted_names[splitted_names.index('github') + 1]

        name = splitted_names[-1]

        if len(splitted_names) == 2:
            return self.find_and_load_module('github', complete_name)
        if len(splitted_names) == 3:
            username_directory = os.path.join(MODULES_PATH, 'github', username)
            if not os.path.exists(username_directory):
                os.mkdir(username_directory)
            username_init_filename = os.path.join(MODULES_PATH, 'github', username, '__init__.py')
            open(username_init_filename, 'a').close()
            return self.find_and_load_module(name, complete_name)
        if len(splitted_names) == 4:
            self.clone_github_repo(username, name)
            return self.find_and_load_module(name, complete_name)
        if len(splitted_names) >= 5:
            return self.find_and_load_module(name, complete_name)


sys.meta_path = [ImportFromGithub()] + sys.meta_path
