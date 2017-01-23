# -*- coding: utf-8 -*-
import os
import sys
import logging
import ipdb

from importlib.abc import SourceLoader

import requests
from git import Repo

from importlib.abc import MetaPathFinder

from packyou import find_module_in_cloned_report


MODULES_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = os.path.join(MODULES_PATH, 'github')
LOGGER = logging.getLogger(__name__)


class GithubFinderAbc(MetaPathFinder):

    def check_username_available(self, username):
        """
            Sometimes github has a - in the username or repository name.
            The - can't be used in the import statement.
        """
        user_profile_url = 'https://github.com/{0}'.format(username)
        response = requests.get(user_profile_url)
        if response.status_code == 404:
            user_profile_url = 'https://github.com/{0}'.format(username.replace('_', '-'))
            response = requests.get(user_profile_url)
            if response.status_code == 200:
                return user_profile_url

    def check_repository_available(self, username, repository_name):
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


class GithubLoader(SourceLoader):

    def __init__(self, fullname, path, repo_url=None):
        self.name = fullname
        if path:
            self.path = path[0]
        self.repo_url = repo_url
        self.username = None
        self.repository_name = None
        self.root_module = None

    def clone_github_repo(self):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = os.path.join(MODULES_PATH, 'github', self.username, self.repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(self.repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

    def get_data(self, path):
        LOGGER.info('get data from {0}'.format(path))
        with open(path, 'r') as data_file:
            return data_file.read()

    def get_filename(self, fullname):
        LOGGER.info('Get filename for {0}. Current Path is {1}'.format(fullname, self.path))
        filename = os.path.join(self.path, '__init__.py')
        if not os.path.exists(filename):
            filename = '{0}.py'.format(self.path)
            if not os.path.exists(filename):
                raise ImportError('Filename {0} not found.'.format(filename))
        return filename

    def load_module(self, fullname):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        LOGGER.info('Loading module {0}'.format(fullname))
        if fullname in sys.modules:
            return sys.modules[fullname]

        splitted_names = fullname.split('.')
        if 'github' in splitted_names:
            if len(splitted_names) >= 3:
                self.username = splitted_names[splitted_names.index('github') + 1]
            if len(splitted_names) >= 4:
                self.repository_name = splitted_names[splitted_names.index('github') + 2]

            if self.username and self.repository_name:
                self.clone_github_repo()

            if len(splitted_names) == 2:
                return super().load_module(fullname)
            if len(splitted_names) == 3:
                username_directory = os.path.join(MODULES_PATH, 'github', self.username)
                if not os.path.exists(username_directory):
                    os.mkdir(username_directory)
                    init_filename = os.path.join(username_directory, '__init__.py')
                    open(init_filename, 'a').close()
                return super().load_module(fullname)
            if len(splitted_names) >= 4:
                module = super().load_module(fullname)
                parent, _, current_module = fullname.rpartition('.')
                root_modules = [
                    'packyou.github.{0}.{1}'.format(self.username, self.repository_name),
                    'packyou.github.{0}.{1}.{1}'.format(self.username, self.repository_name)
                ]
                LOGGER.info('Current module is {0}'.format(current_module))
                if fullname in root_modules:
                    self.root_module = fullname
                    sys.modules[current_module] = module
                return module

        else:
            ipdb.set_trace()
            module = super().load_module(fullname)
            sys.modules[fullname] = module
            if not module:
                raise ImportError
            return module


class GithubFinder(GithubFinderAbc):
    """
        Import hook that will allow to import from the specific loader.
    """
    def find_module_in_cloned_repos(self, fullname):
        return find_module_in_cloned_report(fullname, GithubLoader)

    def find_spec(self, fullname, paths, target=None):
        LOGGER.info('Loading Spec -> {0}'.format(fullname))
        repo_url = None
        if fullname.startswith('packyou.github.'):

            splitted_names = fullname.split('.')

            if len(splitted_names) >= 3:
                username = splitted_names[splitted_names.index('github') + 1]
                if not self.check_username_available(username):
                    return

            if len(splitted_names) >= 4:
                repository_name = splitted_names[splitted_names.index('github') + 2]
                repo_url = self.check_repository_available(username, repository_name)
                if not repo_url:
                    return
            fixed_paths = []
            for path in paths:
                parent, _, current = path.rpartition('/')
                if os.path.exists(os.path.join(path, current)):
                    path = os.path.join(path, current)
                current_module = fullname.rpartition('.')[2]
                module_path = [path]
                if current != current_module:
                    module_path = [path] + [fullname.rpartition('.')[2]]
                fixed_paths.append(os.path.join(*module_path))
            loader = GithubLoader(fullname, fixed_paths, repo_url)
            return loader.load_module(fullname)
        else:
            # we are in the case of relative imports.
            # all the meta_path finders were already executed.
            # we need to search in the repos path for the specified module

            LOGGER.info('Searching in cloned repos')
            found_in_cloned_repos = self.find_module_in_cloned_repos(fullname)
            LOGGER.info('Result found was {0}'.format(found_in_cloned_repos))
            return found_in_cloned_repos


sys.meta_path = [GithubFinder()] + sys.meta_path
