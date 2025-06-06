import pytest

# main.py はGUI主体のため、起動テストのみ簡易的に行う例
import main


def test_run_gui_exists():
    assert hasattr(main, "run_gui")
