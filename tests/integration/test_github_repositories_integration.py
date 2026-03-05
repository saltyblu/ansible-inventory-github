# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import pytest

from plugins.inventory.github_repositories_inventory import GitHubRepositoryFetcher


pytestmark = pytest.mark.integration


def test_fetch_repositories_live_github_api():
    """Integration test against the real GitHub API.

    Required environment variables:
    - GITHUB_TOKEN
    Optional:
    - GITHUB_TEST_ORG (default: "saltyblu")
    - GITHUB_TEST_FILTER (default: "-deployment")
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set")

    org = os.getenv("GITHUB_TEST_ORG", "saltyblu")
    repo_filter = os.getenv("GITHUB_TEST_FILTER", "*-deployment")

    fetcher = GitHubRepositoryFetcher(token)
    repos = fetcher.fetch_repositories(
        repository_filter=repo_filter,
        org=org,
        archived=False,
        group_by_languages=False,
    )

    assert isinstance(repos, list)
    # A valid call should return a list; it can be empty depending on filter/org visibility.
    if repos:
        assert "name" in repos[0]
        assert "languages" in repos[0]
        assert repos[0]["languages"] is None
