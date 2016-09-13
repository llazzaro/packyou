# -*- coding: utf-8 -*-
import os
import sys
from importlib.machinery import PathFinder

import requests

from git import Repo

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))


class ImportFromGithub(object):
    """
        Import hook that will allow to import from a  github repo.
    """
    def __init__(self):
        self.path = None

    def find_module(self, fullname, path=None):
        """
            Finds a module and returns a module loader when
            the import uses packyou
        """
        self.path = path
        return self

    def find_and_load_module(self, complete_name):
        """
            Given a name and a path it will return a module instance
            if found.
            When the module could not be found it will raise ImportError
        """
        if complete_name in sys.modules:
            return sys.modules[complete_name]
        module = None
        module_spec = PathFinder.find_spec(complete_name)
        if module_spec:
            loader = module_spec.loader
            module = loader.load_module()
            sys.modules[complete_name] = module
        return module

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

    def clone_github_repo(self, username, repository_name):
        """
            Clones a github repo with a username and repository_name
        """
        repo_url = self.check_repository_available(username, repository_name)
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

        self.update_sys_path()

    def update_sys_path(self):
        """
            Iterates over all cloned repos and add them to the syspath.
            This was required since cloned project uses relative imports.
        """
        github_repos_path = os.path.join(MODULES_PATH, 'github')
        for file_or_directory in os.walk(github_repos_path):
            if os.path.isdir(file_or_directory[0]) or os.path.splitext(file_or_directory[0])[1] in ['.py', '.pyc']:
                if file_or_directory[0] not in sys.path:
                    sys.path.append(file_or_directory[0])

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
                self.update_sys_path()
                return self.find_and_load_module(complete_name)
            if len(splitted_names) == 3:
                username_directory = os.path.join(MODULES_PATH, 'github', username)
                if not os.path.exists(username_directory):
                    os.mkdir(username_directory)
                username_init_filename = os.path.join(MODULES_PATH, 'github', username, '__init__.py')
                open(username_init_filename, 'a').close()
                return self.find_and_load_module(complete_name)
            if len(splitted_names) >= 4:
                return self.find_and_load_module(complete_name)

        else:
            self.update_sys_path()
            module = self.find_and_load_module(complete_name)
            if not module:
                raise ImportError
            return module


sys.meta_path.append(ImportFromGithub())
