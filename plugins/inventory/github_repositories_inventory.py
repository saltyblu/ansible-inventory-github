# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from github import Github
import re
import logging
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable
from ansible.inventory.group import to_safe_group_name

DOCUMENTATION = '''
    author:
        - Volker Schmitz (saltyblu)
        - Martin Soentgenrath (merin80)
    name: github-repository-inventory
    short_description: GitHub repositories as inventory source
    version_added: 0.0.0
    description:
        - Get repositories from the GitHub API and store them as hosts.
        - The primary IP addresses contains the Git Repository clone url.
    extends_documentation_fragment:
        - inventory_cache
    options:
        url:
            description: GitHub URL.
            default: 'https://github.com/'
            env:
                - name: GITHUB_INVENTORY_URL
        access_token:
            description: GitHub authentication PAT.
            required: true
            env:
                - name: GITHUB_INVENTORY_ACCESS_TOKEN
        org:
            description: GitHub organization.
            required: true
            env:
                - name: GITHUB_INVENTORY_ORG
        repository_filter:
            description: Repository Filter
            default: ""
            env:
                - name: GITHUB_INVENTORY_SEARCH_FILTER
        cache:
            description: The Cache option
            required: false
            default: False
        group_by_languages:
            description: Load all language Informations from github Repos and group the repositories by Language
            default: false
            env:
                - name: GITHUB_INVENTORY_GROUP_BY_LANGUAGES
        regex_filter:
            description: A regexp which allows grouping of the inventory. For that the pattern will be applied on the repository.name and if a match is found all regex groups matches will be added as group name for the repository
            default: ""
            env:
                - name: GITHUB_INVENTORY_REGEX_GROUP_FILTER
        show_archived_repos:
            description: Exclude archived repos in search, boolean.
            default: false
            env:
                - name: GITHUB_INVENTORY_ARCHIVED
'''

EXAMPLES = '''
# github-inventory.yml
access_token: secure
org: saltyblu
repository_filter: *-deployment
'''

class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using GitHub as source. '''

    NAME = 'github_repositories_inventory'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.cache_key = None
        self.connection = None
        logging.basicConfig(filename="dynamic_inventory.log",
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.INFO)

        self.logger = logging.getLogger('DynamicInventory')

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('github_repositories.yaml', 'github_repositories.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending with "github_repositories.yaml/.yml"')
        return valid

    def parse_groupnames(self, repository, regex_filter):
        try:
            matches = re.findall(regex_filter, repository['name'])
            if matches:
                result = []
                main_group = f'main-{matches[0][0]}'
                if main_group:
                    result.append(main_group)
                for match in matches:
                    result.extend(match)
                return result
            else:
                return False
        except Exception as e:
            self.logger.debug(f'Exception while parsing groups: {e}')
            return False

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self.load_cache_plugin()
        cache_key = self.get_cache_key(path)
        self.logger.debug(f'The Cache Key is: {cache_key}')

        # read config from file, this sets 'options'
        self._read_config_data(path)

        user_cache_setting = self.get_option('cache')
        self.logger.debug(f'User Cache Setting is: {user_cache_setting}')
        # read if the user has caching enabled and the cache isn't being refreshed
        attempt_to_read_cache = user_cache_setting and cache
        self.logger.debug(f'Attempt to read cache is: {attempt_to_read_cache}')
        # update if the user has caching enabled and the cache is being refreshed; update this value to True if the cache has expired below
        cache_needs_update = user_cache_setting and not cache
        self.logger.debug(f'Cache needs update is: {cache_needs_update}')

        # get connection host
        self.github_url = str(self.get_option('url'))
        self.access_token = str(self.get_option('access_token'))
        self.org = str(self.get_option('org'))
        self.repository_filter = str(self.get_option('repository_filter'))
        self.regex_filter = str(self.get_option('regex_filter'))
        self.archived = bool(self.get_option('show_archived_repos'))
        self.group_by_languages = bool(self.get_option('group_by_languages'))

        if attempt_to_read_cache:
            self.logger.debug("Attempting to read cache")
            try:
                results = self._cache[cache_key]
                self.logger.debug(f'Results: {results}')
            except KeyError as e:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True
                self.logger.error(f'Exception while Updating cache: {e}')
        if not attempt_to_read_cache or cache_needs_update or not results:
            self.logger.debug("Not attempting to read cache")
            # parse the provided inventory source
            results = self.get_repositories()
            self.logger.debug(f'Results: {results}')
        if cache_needs_update:
            try:
                self._cache[cache_key] = results
                self.logger.debug(f'Cached Result as: {self._cache}')
            except Exception as e:
                self.logger.error(f'Exception on Cache Update: {e}')

        self.populate(results)

    def get_repositories(self):
        count = 1
        g = Github(self.access_token)
        repos = []
        try:
            r = g.search_repositories(query=self.repository_filter, owner=self.org, sort="updated", archived=self.archived)
        except Exception as e:
            self.logger.error(f'Caught an Exception while searching: {e}')
            print(
                f"Error: {e}",
            )
            return
        try:
            for repository in r:
                repo_raw_data = repository._rawData
                self.logger.debug(f"Group by Language is: {self.group_by_languages}")
                if self.group_by_languages:
                    repo_raw_data['languages'] = repository.get_languages()
                else:
                    repo_raw_data['languages'] = None
                self.logger.debug(f'Counter: {count} - {repository.name}')
                repos.append(repo_raw_data)
                count += 1
            return repos
        except Exception as e:
            self.logger.error(f'Caught an Exception while iterating Repositories: {e}')

    def populate(self, r):
        try:
            # add main group as inventory group
            group = "all"
            for project in r:

                groupnames = []
                topics = project['topics']
                team = next((topic for topic in topics if topic.startswith("team-")), None)
                if team is not None:
                    groupnames.append(team)
                else:
                    groupnames.append("unassigned")

                self.logger.debug(f'regex_filter: {self.regex_filter}')
                if self.regex_filter != "":
                    regex_groups = self.parse_groupnames(project, self.regex_filter)
                    if regex_groups:
                        for group in regex_groups:
                            groupnames.append(group)
                else:
                    if "unassigned" not in groupnames:
                        groupnames.append("unassigned")
                self.logger.debug(f'Name: {project["name"]}')
                if self.group_by_languages:
                    for key, value in project['languages'].items():
                        group = self.inventory.add_group(to_safe_group_name(f'{key.lower().replace(" ", "")}', force=True, silent=True))
                        hostname = self.inventory.add_host(str(project['name']), group)
                for groupentry in groupnames:
                    group = self.inventory.add_group(str(groupentry).replace("-", "_"))

                    hostname = self.inventory.add_host(str(project['name']), group)

                self.inventory.set_variable(hostname, 'ansible_host', 'localhost')
                self.inventory.set_variable(hostname, 'ansible_connection', 'local')
                for key, value in project.items():
                    self.inventory.set_variable(hostname, key, value)
                if team is not None:
                    self.inventory.set_variable(hostname, 'team', team)

        except Exception as e:
            self.logger.error(f'Exception: {e}')
            print(
                f"Error: {e}",
            )
            return
