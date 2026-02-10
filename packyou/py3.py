# -*- coding: utf-8 -*-
import os
import sys
import logging
from pathlib import Path

from importlib.abc import SourceLoader, MetaPathFinder

import requests
from git import Repo

from packyou import find_module_path_in_cloned_repos


MODULES_PATH = str(Path(__file__).parent)
GITHUB_REPOSITORIES_DIRECTORY = str(Path(MODULES_PATH) / 'github')
LOGGER = logging.getLogger(__name__)


class GithubFinderAbc(MetaPathFinder):

    def check_username_available(self, username):
        """
            Sometimes github has a - in the username or repository name.
            The - can't be used in the import statement.
        """
        user_profile_url = f'https://github.com/{username}'
        response = requests.get(user_profile_url)
        if response.status_code == 404:
            user_profile_url = f'https://github.com/{username.replace("_", "-")}'
            response = requests.get(user_profile_url)
            if response.status_code == 200:
                return user_profile_url

    def check_repository_available(self, username, repository_name):
        repo_url = f'https://github.com/{username}/{repository_name}.git'
        response = requests.get(repo_url)
        if response.status_code == 404:
            if '_' in username:
                repo_url = f'https://github.com/{username.replace("_", "-")}/{repository_name}.git'
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url
            if '_' in repository_name:
                repo_url = f'https://github.com/{username}/{repository_name.replace("_", "-")}.git'
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url

            repo_url = f'https://github.com/{username.replace("_", "-")}/{repository_name.replace("_", "-")}.git'
            response = requests.get(repo_url)
            if response.status_code == 200:
                return repo_url
            raise ImportError('Github repository not found.')

        return repo_url


class GithubLoader(SourceLoader):

    def __init__(self, fullname, path, repo_url=None):
        self.github_token = token = os.environ.get("GITHUB_TOKEN")

        if not token:
            self.repo_url = repo_url
        else:
            base = repo_url[len("https://"):]
            self.repo_url = f"https://{token}:x-oauth-basic@{base}"

        self.name = fullname
        if path:
            self.path = path[0]
        self.username = None
        self.repository_name = None
        self.root_module = None

    def clone_github_repo(self):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = str(Path(MODULES_PATH) / 'github' / self.username / self.repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(self.repo_url, repository_local_destination, branch='master')
            init_filename = str(Path(repository_local_destination) / '__init__.py')
            Path(init_filename).touch()

    def get_data(self, path):
        LOGGER.info(f'get data from {path}')
        with open(path, 'r') as data_file:
            return data_file.read()

    def get_filename(self, fullname):
        LOGGER.info(f'Get filename for {fullname}. Current Path is {self.path}')
        filename = str(Path(self.path) / '__init__.py')
        if not os.path.exists(filename):
            filename = f'{self.path}.py'
            if not os.path.exists(filename):
                raise ImportError(f'Filename {filename} not found.')
        return filename

    def load_module(self, fullname):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        LOGGER.info(f'Loading module {fullname}')
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
                username_directory = str(Path(MODULES_PATH) / 'github' / self.username)
                if not os.path.exists(username_directory):
                    os.mkdir(username_directory)
                    init_filename = str(Path(username_directory) / '__init__.py')
                    Path(init_filename).touch()
                return super().load_module(fullname)
            if len(splitted_names) >= 4:
                module = super().load_module(fullname)
                parent, _, current_module = fullname.rpartition('.')
                root_modules = [
                    f'packyou.github.{self.username}.{self.repository_name}',
                    f'packyou.github.{self.username}.{self.repository_name}.{self.repository_name}'
                ]
                LOGGER.info(f'Current module is {current_module}')
                if fullname in root_modules:
                    self.root_module = fullname
                    sys.modules[current_module] = module
                return module

        else:
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
        return find_module_path_in_cloned_repos(fullname)

    def find_spec(self, fullname, paths, target=None):
        LOGGER.info(f'Loading Spec -> {fullname}')
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
            # Only search cloned repos for imports that aren't part of packyou itself
            if fullname.startswith('packyou.') or fullname == 'packyou':
                return None
            LOGGER.info('Searching in cloned repos')
            found_paths, remaining = self.find_module_in_cloned_repos(fullname)
            LOGGER.info(f'Result found was {found_paths}')
            if found_paths and not remaining:
                loader = GithubLoader(fullname, found_paths)
                return loader.load_module(fullname)
            return None


sys.meta_path = [GithubFinder()] + sys.meta_path
