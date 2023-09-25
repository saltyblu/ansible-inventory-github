# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

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
                - name: GITHUB_URL
        access_token:
            description: GitHub authentication PAT.
            required: true
            env:
                - name: GITHUB_ACCESS_TOKEN
        org:
            description: GitHub organization.
            required: true
            env:
                - name: GITHUB_ORG
        search_filter:
            description: Repository Filter
            default: ""
        cache:
            description: The Cache option
            required: false
            default: False
        regex_filter:
            description: A regexp which allows grouping of the inventory. For that the pattern will be applied on the repository.name and if a match is found the first match will be the group name for the repository
            default: ""
'''

EXAMPLES = '''
# github-inventory.yml
access_token: secure
org: saltyblu
repository_filter: *-deployment
'''

from github import Github
import re
#from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name

class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using GitHub as source. '''

    NAME = 'github_repositories'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.cache_key = None
        self.connection = None

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('github_repositories.yaml', 'github_repositories.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending with "github-inventory.yaml/.yml"')
        return valid

    #def _init_cache(self):
    #    if self.cache_key not in self._cache:
    #        self._cache[self.cache_key] = {}

    #def _reload_cache(self):
    #    if self.get_option('cache_fallback'):
    #        self.display.vvv('Cannot connect to server, loading cache\n')
    #        self._options['cache_timeout'] = 0
    #        self.load_cache_plugin()
    #        self._cache.get(self.cache_key, {})

    # def extract_codeowner(self, repository):
    #     try:
    #         codeowners_file = repository.get_contents("CODEOWNERS")
    #         codeowners_content = codeowners_file.decoded_content.decode('utf-8')
    #         codeowners = [line.strip() for line in codeowners_content.split('\n') if line.strip().startswith('* ')]
    #         return codeowners[0].replace("* ", "").replace("@", "").replace("/", "_").replace("-", "_").split(" ")
    #     except Exception as e:
    #         return False

    def parse_groupname(self, repository, regex_filter):
        try:
            match = re.findall(regex_filter, repository.name)
            return match[0]
        except Exception as e:
            return False


    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self.load_cache_plugin()
        cache_key = self.get_cache_key(path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        user_cache_setting = self.get_option('cache')
        # read if the user has caching enabled and the cache isn't being refreshed
        attempt_to_read_cache = user_cache_setting and cache
        # update if the user has caching enabled and the cache is being refreshed; update this value to True if the cache has expired below
        cache_needs_update = user_cache_setting and not cache

        # get connection host
        self.github_url = str(self.get_option('url'))
        self.access_token = str(self.get_option('access_token'))
        self.org = str(self.get_option('org'))
        self.repository_filter = str(self.get_option('search_filter'))
        self.regex_filter = str(self.get_option('regex_filter'))
        #self.repository_filter = str(self.get_option('repository_filter'))
        #self.cache_key = self.get_cache_key(path)
        #self.use_cache = cache and self.get_option('cache')
        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True
        if not attempt_to_read_cache or cache_needs_update:
            # parse the provided inventory source
            results = self.get_inventory()
        if cache_needs_update:
            self._cache[cache_key] = results

        self.populate(results)

    def get_inventory(self):
        g = Github(self.access_token)
        try:
            r = g.search_repositories(self.repository_filter, owner=self.org)
        except Exception as e:
            print(
                f"Error: {e}",
            )
            return
        return r

    def populate(self, r):
        try:
            # add main group as inventory group
            group = "all"
            for project in r:
                if not project.name.startswith(self.repository_filter):
                    continue

                groupnames = []
                topics = project._rawData['topics']
                team = next((topic for topic in topics if topic.startswith("team-")), None)
                if team != None:
                    groupnames.append(team)
                else:
                    groupnames.append("unassigned")

                if self.regex_filter != "":
                    groupnames.append(self.parse_groupname(project, self.regex_filter))
                else:
                    if not "unassigned" in groupnames:
                        groupnames.append("unassigned")
                for groupentry in groupnames:
                    group = self.inventory.add_group(str(groupentry).replace("-", "_"))

                    hostname = self.inventory.add_host(str(project.id), group)
                    # add basic vars to host
                    self.inventory.set_variable(hostname, 'ansible_host', 'localhost')
                    self.inventory.set_variable(hostname, 'git_url', project.ssh_url)
                    self.inventory.set_variable(hostname, 'git_name', project.name)
                    self.inventory.set_variable(hostname, 'git_html_url', project.html_url)
                    self.inventory.set_variable(hostname, 'topics', topics)
                # if self.group_by_codeowners and codeowners:
                #     self.inventory.set_variable(hostname, 'codeowners', codeowners)

                # add all infos of gitlab api to host as vars
                #for attr, value in project.__dict__.items():
                #    self.inventory.set_variable(project.ssh_url_to_repo, attr, value)
        except Exception as e:
            print(
                f"Error: {e}",
            )
            return
