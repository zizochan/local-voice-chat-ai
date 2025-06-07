import pytest
import gui


def test_create_speaker_dropdown_exists():
    assert hasattr(gui, "create_speaker_dropdown")


def test_create_model_dropdown_exists():
    assert hasattr(gui, "create_model_dropdown")


def test_run_gui_exists():
    assert hasattr(gui, "run_gui")
