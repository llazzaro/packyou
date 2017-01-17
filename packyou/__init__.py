import sys
import requests
from importlib.abc import MetaPathFinder


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

if (sys.version_info > (3, 0)):
    # Python 3
    from packyou import py3
else:
    # Python 2
    from packyou import py2
