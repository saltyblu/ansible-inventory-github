# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import logging
from unittest.mock import Mock

from plugins.inventory.github_repositories_inventory import (
    GitHubRepositoryFetcher,
    get_logger,
)


class TestGetLogger:
    """Test the get_logger helper function."""

    def test_get_logger_with_none_creates_new_logger(self):
        """Test that get_logger creates a new logger when passed None."""
        logger = get_logger('test_logger', None)
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'

    def test_get_logger_returns_provided_logger(self):
        """Test that get_logger returns the provided logger."""
        mock_logger = Mock()
        result = get_logger('test_logger', mock_logger)
        assert result is mock_logger


class TestGitHubRepositoryFetcher:
    """Test the GitHubRepositoryFetcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.access_token = 'test_token_123'
        self.mock_logger = Mock(spec=logging.Logger)

    def test_initialization(self):
        """Test GitHubRepositoryFetcher initialization."""
        fetcher = GitHubRepositoryFetcher(self.access_token, self.mock_logger)
        assert fetcher.access_token == self.access_token
        assert fetcher.logger is self.mock_logger
        assert fetcher._github_client is None

    def test_initialization_without_logger(self):
        """Test GitHubRepositoryFetcher initialization without logger."""
        fetcher = GitHubRepositoryFetcher(self.access_token)
        assert fetcher.access_token == self.access_token
        assert isinstance(fetcher.logger, logging.Logger)

    def test_set_github_client(self):
        """Test setting a custom GitHub client."""
        fetcher = GitHubRepositoryFetcher(self.access_token, self.mock_logger)
        mock_client = Mock()
        fetcher.set_github_client(mock_client)
        assert fetcher._github_client is mock_client

    def test_fetch_repositories_returns_list(self):
        """Test that fetch_repositories returns a list of repositories."""
        fetcher = GitHubRepositoryFetcher(self.access_token, self.mock_logger)

        # Mock GitHub client and search result
        mock_github = Mock()
        mock_repo1 = Mock()
        mock_repo1._rawData = {'name': 'repo1', 'id': 1}
        mock_repo1.get_languages.return_value = {'Python': 100}

        mock_repo2 = Mock()
        mock_repo2._rawData = {'name': 'repo2', 'id': 2}
        mock_repo2.get_languages.return_value = {'Go': 100}

        mock_search_result = [mock_repo1, mock_repo2]
        mock_github.search_repositories.return_value = mock_search_result

        fetcher.set_github_client(mock_github)

        result = fetcher.fetch_repositories(
            repository_filter='test-*',
            org='test-org',
            archived=False,
            group_by_languages=True
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['name'] == 'repo1'
        assert result[0]['languages'] == {'Python': 100}
        assert result[1]['name'] == 'repo2'
        assert result[1]['languages'] == {'Go': 100}

    def test_fetch_repositories_without_languages(self):
        """Test fetch_repositories without language information."""
        fetcher = GitHubRepositoryFetcher(self.access_token, self.mock_logger)

        mock_github = Mock()
        mock_repo = Mock()
        mock_repo._rawData = {'name': 'repo1', 'id': 1}

        mock_search_result = [mock_repo]
        mock_github.search_repositories.return_value = mock_search_result

        fetcher.set_github_client(mock_github)

        result = fetcher.fetch_repositories(
            repository_filter='test-*',
            org='test-org',
            group_by_languages=False
        )

        assert len(result) == 1
        assert result[0]['languages'] is None

    def test_fetch_repositories_search_error(self):
        """Test fetch_repositories handles search errors."""
        fetcher = GitHubRepositoryFetcher(self.access_token, self.mock_logger)

        mock_github = Mock()
        mock_github.search_repositories.side_effect = Exception('API Error')

        fetcher.set_github_client(mock_github)

        with pytest.raises(Exception) as exc_info:
            fetcher.fetch_repositories(
                repository_filter='test-*',
                org='test-org'
            )

        assert 'API Error' in str(exc_info.value)
        self.mock_logger.error.assert_called()


class TestInventoryModuleParseMethods:
    """Test parse_groupnames and other inventory logic."""

    def test_parse_groupnames_with_match(self):
        """Test parse_groupnames with regex matches."""
        from plugins.inventory.github_repositories_inventory import InventoryModule

        inventory = InventoryModule(logger=Mock())
        repository = {'name': 'main-prod-api'}

        # Test regex that captures environment and service type
        regex_filter = r'(prod|staging)-(.*)'
        result = inventory.parse_groupnames(repository, regex_filter)

        assert result is not False
        assert isinstance(result, list)
        assert 'main-prod' in result

    def test_parse_groupnames_no_match(self):
        """Test parse_groupnames with no matches."""
        from plugins.inventory.github_repositories_inventory import InventoryModule

        inventory = InventoryModule(logger=Mock())
        repository = {'name': 'random-repo'}

        regex_filter = r'(prod|staging)-(.*)'
        result = inventory.parse_groupnames(repository, regex_filter)

        assert result is False

    def test_parse_groupnames_invalid_regex(self):
        """Test parse_groupnames handles invalid regex gracefully."""
        from plugins.inventory.github_repositories_inventory import InventoryModule

        mock_logger = Mock()
        inventory = InventoryModule(logger=mock_logger)
        repository = {'name': 'test-repo'}

        # Invalid regex pattern
        regex_filter = r'(invalid['
        result = inventory.parse_groupnames(repository, regex_filter)

        assert result is False
        mock_logger.debug.assert_called()


class TestInventoryModuleIntegration:
    """Integration tests for InventoryModule with mocked fetcher."""

    def test_inventory_module_with_custom_fetcher(self):
        """Test InventoryModule using custom fetcher."""
        from plugins.inventory.github_repositories_inventory import (
            InventoryModule,
            GitHubRepositoryFetcher,
        )

        mock_logger = Mock()
        mock_fetcher = Mock(spec=GitHubRepositoryFetcher)
        mock_fetcher.fetch_repositories.return_value = [
            {'name': 'repo-1', 'topics': ['team-backend']},
            {'name': 'repo-2', 'topics': []},
        ]

        inventory = InventoryModule(logger=mock_logger, fetcher=mock_fetcher)

        # Verify that custom fetcher is stored
        assert inventory.fetcher is mock_fetcher
        assert inventory.logger is mock_logger
