"""Tests for CLI functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from anime_downloader.cli.commands import parse_episode_selection, get_anime_dir, get_video_path, choose_anime


class TestEpisodeSelection:
    """Test cases for episode selection parsing."""

    def test_single_episode(self):
        """Test parsing single episode."""
        result = parse_episode_selection("5", 10)
        assert result == [5]

    def test_multiple_episodes(self):
        """Test parsing multiple episodes."""
        result = parse_episode_selection("1, 3, 5", 10)
        assert result == [1, 3, 5]

    def test_episode_range(self):
        """Test parsing episode range."""
        result = parse_episode_selection("1-5", 10)
        assert result == [1, 2, 3, 4, 5]

    def test_mixed_selection(self):
        """Test parsing mixed selection."""
        result = parse_episode_selection("1, 3-5, 8", 10)
        assert result == [1, 3, 4, 5, 8]

    def test_reverse_range(self):
        """Test parsing reverse range."""
        result = parse_episode_selection("5-3", 10)
        assert result == [3, 4, 5]

    def test_out_of_range(self):
        """Test handling out of range episodes."""
        result = parse_episode_selection("1, 15, 20", 10)
        assert result == [1]

    def test_invalid_input(self):
        """Test handling invalid input."""
        result = parse_episode_selection("1, abc, 3", 10)
        assert result == [1, 3]

    def test_empty_input(self):
        """Test handling empty input."""
        result = parse_episode_selection("", 10)
        assert result == []


class TestPathHelpers:
    """Test cases for path helper functions."""

    def test_get_anime_dir(self):
        """Test anime directory path generation."""
        path = get_anime_dir("Test Anime", "/downloads")
        assert "Test Anime" in path
        assert "/downloads" in path

    def test_get_video_path(self):
        """Test video file path generation."""
        path = get_video_path("Test Anime", 5, "/downloads")
        assert "Test Anime" in path
        assert "Episode 5" in path
        assert path.endswith(".mp4")


class TestMultiSelection:
    """Test cases for multi-selection functionality."""

    @patch('anime_downloader.cli.commands._questionary_select')
    def test_choose_anime_single_selection(self, mock_select):
        """Test single anime selection (with --single flag)."""
        mock_api = Mock()
        anime1 = {"title": "Anime 1", "session": "anime-1"}
        mock_api.search.return_value = [
            anime1,
            {"title": "Anime 2", "session": "anime-2"},
        ]

        # Single-select returns a single value (the chosen result dict).
        mock_select.return_value = anime1

        result = choose_anime(mock_api, "test", multi=False)

        assert result is not None
        assert len(result) == 1
        assert result[0]["title"] == "Anime 1"
        assert result[0]["session"] == "anime-1"
        # Single mode should request a non-multi prompt.
        assert mock_select.call_args[0][2] is False

    @patch('anime_downloader.cli.commands._questionary_select')
    def test_choose_anime_multi_selection(self, mock_select):
        """Test multiple anime selection (default behavior)."""
        mock_api = Mock()
        anime1 = {"title": "Anime 1", "session": "anime-1"}
        anime3 = {"title": "Anime 3", "session": "anime-3"}
        mock_api.search.return_value = [
            anime1,
            {"title": "Anime 2", "session": "anime-2"},
            anime3,
        ]

        # Multi-select returns a list of chosen result dicts.
        mock_select.return_value = [anime1, anime3]

        result = choose_anime(mock_api, "test", multi=True)

        assert result is not None
        assert len(result) == 2
        assert result[0]["title"] == "Anime 1"
        assert result[1]["title"] == "Anime 3"
        # Multi mode should request a multi-select prompt.
        mock_select.assert_called_once()
        assert mock_select.call_args[0][2] is True

    @patch('anime_downloader.cli.commands._questionary_select')
    def test_choose_anime_no_results(self, mock_select):
        """Test behavior when no anime are found."""
        mock_api = Mock()
        mock_api.search.return_value = []

        result = choose_anime(mock_api, "nonexistent", multi=True)

        assert result is None
        mock_select.assert_not_called()

    @patch('anime_downloader.cli.commands._questionary_select')
    def test_choose_anime_no_selection(self, mock_select):
        """Test behavior when user cancels selection."""
        mock_api = Mock()
        mock_api.search.return_value = [
            {"title": "Anime 1", "session": "anime-1"},
        ]

        mock_select.return_value = None

        result = choose_anime(mock_api, "test", multi=True)

        assert result is None
