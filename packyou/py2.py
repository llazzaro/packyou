# -*- coding: utf-8 -*-
import imp
import sys

from sys import modules, path, meta_path
from os import walk, mkdir
from os.path import (
    isdir,
    abspath,
    dirname,
    exists,
    join,
    splitext
)

import encodings.idna
import requests

from git import Repo
from packyou.utils import get_filename, get_source

MODULES_PATH = dirname(abspath(__file__))


class GithubLoader(object):
    """
        Import hook that will allow to import from a  github repo.
    """
    def __init__(self, repo_url=None, path=None):
        self.path = path
        self.repo_url = repo_url

    def is_package(self, fullname):
        filename = get_filename(fullname)
        return not exists(filename) or isdir(filename)

    def get_or_create_module(self, fullname):
        """
            Given a name and a path it will return a module instance
            if found.
            When the module could not be found it will raise ImportError
        """
        print('loading module', fullname)
        parent, _, module_name = fullname.rpartition('.')
        if fullname in modules:
            return modules[fullname]

        if module_name in modules:
            return modules[module_name]

        module = modules.setdefault(fullname, imp.new_module(fullname))
        if len(fullname.strip('.')) > 3:
            absolute_from_root = fullname.split('.', 3)[-1]
            modules.setdefault(absolute_from_root, module)
        if len(fullname.split('.')) == 4:
            # add the root of the project
            modules[fullname.split('.')[-1]] = module
        # required by PEP 302
        module.__file__ = get_filename(fullname)
        module.__name__ = fullname
        module.__loader__ = self
        module.__path__ = self.path
        if self.is_package(fullname):
            module.__path__ = self.path
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]

        try:
            print('loading file ', get_filename(fullname))
            source = get_source(fullname)
        except IOError:
            # fall back to absolute import
            absolute_name = fullname.split('.')[-1]
            if absolute_name not in modules and absolute_from_root not in modules:
                raise ImportError('File not found {0}'.format(get_filename(fullname)))
            if absolute_name in modules:
                return modules[absolute_name]
                print('absolute name', absolute_name)
            if absolute_from_root in modules:
                print('absolute root', absolute_from_root)
                return modules[absolute_from_root]

        print('exec ', module.__package__)
        exec(source, module.__dict__)
        return module

    def clone_github_repo(self, username, repository_name):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = join(MODULES_PATH, 'github', username, repository_name)
        if not exists(repository_local_destination):
            Repo.clone_from(self.repo_url, repository_local_destination, branch='master')
            init_filename = join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

    def load_module(self, name):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        complete_name = name
        splitted_names = name.split('.')
        username = None
        repository_name = None
        name = splitted_names[-1]
        if 'github' in splitted_names:
            if len(splitted_names) >= 3:
                username = splitted_names[splitted_names.index('github') + 1]
            if len(splitted_names) >= 4:
                repository_name = splitted_names[splitted_names.index('github') + 2]

            if username and repository_name:
                self.clone_github_repo(username, repository_name)
            if len(splitted_names) == 2:
                return self.get_or_create_module(complete_name)
            if len(splitted_names) == 3:
                username_directory = join(MODULES_PATH, 'github', username)
                if not exists(username_directory):
                    mkdir(username_directory)
                username_init_filename = join(MODULES_PATH, 'github', username, '__init__.py')
                open(username_init_filename, 'a').close()
                return self.get_or_create_module(complete_name)
            if len(splitted_names) >= 4:
                return self.get_or_create_module(complete_name)

        else:
            # Here we try to load a module that has a relative import.
            module = self.get_or_create_module(complete_name)
            if not module:
                raise ImportError
            return module


class GithubFinder(object):

    def check_repository_available(self, username, repository_name):
        """
            Sometimes github has a - in the username or repository name.
            The - can't be used in the import statement.
        """
        repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name)
        response = requests.get(repo_url)
        if response.status_code == 404:
            if '_' in username:
                repo_url = 'https://github.com/{0}/{1}.git'.format(username.replace('_', '-'), repository_name)
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url
            if '_' in repository_name:
                repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name.replace('_', '-'))
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url

            repo_url = 'https://github.com/{0}/{1}.git'.format(username.replace('_', '-'), repository_name.replace('_', '-'))
            response = requests.get(repo_url)
            if response.status_code == 200:
                return repo_url
            raise ImportError('Github repository not found.')

        return repo_url

    def find_module(self, fullname, path=None):
        """
            Finds a module and returns a module loader when
            the import uses packyou
        """
        print('Finding ', fullname)
        partent, _, module_name = fullname.rpartition('.')
        try:
            # sometimes the project imported from github does an
            # "import x", this translates to import github...x
            # we try first to do an import x first and return None
            # to let other python finders in the meta_path to do the import
            module_info = imp.find_module(module_name)
            return None
        except ImportError:
            module = None

        if 'packyou.github' in fullname:
            fullname_parts = fullname.split('.')
            repo_url = None
            if len(fullname_parts) >= 4:
                username = fullname.split('.')[2]
                repository_name = fullname.split('.')[3]
                repo_url = self.check_repository_available(username, repository_name)
            return GithubLoader(repo_url, path)


meta_path.append(GithubFinder())
