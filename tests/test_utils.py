import os
import pytest
from unittest.mock import MagicMock, patch

from packyou.utils import walklevel, TQDMCloneProgress, memoize


class TestWalklevel:

    def test_single_level_walk(self, tmp_path):
        """walklevel with level=1 should yield root and one level of subdirs."""
        sub1 = tmp_path / "sub1"
        sub1.mkdir()
        sub2 = tmp_path / "sub2"
        sub2.mkdir()
        deep = sub1 / "deep"
        deep.mkdir()
        (tmp_path / "file.txt").touch()
        (sub1 / "file1.txt").touch()
        (deep / "deepfile.txt").touch()

        results = list(walklevel(str(tmp_path), level=1))

        root_dirs = results[0][1]
        assert "sub1" in root_dirs
        assert "sub2" in root_dirs

        all_roots = [r[0] for r in results]
        assert str(tmp_path) in all_roots
        assert str(sub1) in all_roots
        assert str(sub2) in all_roots
        # deep should NOT appear since level=1
        assert str(deep) not in all_roots

    def test_nonexistent_dir_raises(self):
        """walklevel should raise AssertionError for non-existent directories."""
        with pytest.raises(AssertionError):
            list(walklevel("/nonexistent/path/that/does/not/exist"))

    def test_depth_zero(self, tmp_path):
        """walklevel with level=0 should only yield the root directory."""
        sub = tmp_path / "sub"
        sub.mkdir()

        results = list(walklevel(str(tmp_path), level=0))
        assert len(results) == 1
        assert results[0][0] == str(tmp_path)

    def test_deeper_level(self, tmp_path):
        """walklevel with level=2 should descend two levels."""
        sub = tmp_path / "sub"
        sub.mkdir()
        deep = sub / "deep"
        deep.mkdir()
        very_deep = deep / "verydeep"
        very_deep.mkdir()

        results = list(walklevel(str(tmp_path), level=2))
        all_roots = [r[0] for r in results]
        assert str(tmp_path) in all_roots
        assert str(sub) in all_roots
        assert str(deep) in all_roots
        assert str(very_deep) not in all_roots


class TestTQDMCloneProgress:

    def test_initialization(self):
        """TQDMCloneProgress should initialize with no progress bar."""
        progress = TQDMCloneProgress()
        assert progress.progress is None

    @patch('packyou.utils.tqdm')
    def test_update_creates_progress_bar(self, mock_tqdm):
        """First update call should create a tqdm progress bar."""
        mock_bar = MagicMock()
        mock_tqdm.return_value = mock_bar

        progress = TQDMCloneProgress()
        progress.update(0, 10, 100, '')

        mock_tqdm.assert_called_once_with(total=100)
        mock_bar.update.assert_called_once_with(n=10)

    @patch('packyou.utils.tqdm')
    def test_update_reuses_progress_bar(self, mock_tqdm):
        """Subsequent update calls should reuse the existing progress bar."""
        mock_bar = MagicMock()
        mock_tqdm.return_value = mock_bar

        progress = TQDMCloneProgress()
        progress.update(0, 10, 100, '')
        progress.update(0, 50, 100, '')

        assert mock_tqdm.call_count == 1
        assert mock_bar.update.call_count == 2


class TestMemoize:

    def test_caches_result(self):
        """memoize should cache function results."""
        call_count = 0

        @memoize
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive(5) == 10
        assert expensive(5) == 10
        assert call_count == 1

    def test_different_args_not_cached(self):
        """memoize should compute separately for different args."""
        call_count = 0

        @memoize
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive(5) == 10
        assert expensive(10) == 20
        assert call_count == 2

    def test_multiple_args(self):
        """memoize should handle multiple positional args."""
        @memoize
        def add(a, b):
            return a + b

        assert add(1, 2) == 3
        assert add(1, 2) == 3
        assert add(3, 4) == 7
