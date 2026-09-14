from unittest.mock import patch

from app.cleanup import confirm_cleanup


def test_confirmation_yes():

    with patch("builtins.input", return_value="y"):

        assert confirm_cleanup() is True


def test_confirmation_yes_full_word():

    with patch("builtins.input", return_value="yes"):

        assert confirm_cleanup() is True


def test_confirmation_no():

    with patch("builtins.input", return_value="n"):

        assert confirm_cleanup() is False


def test_confirmation_empty():

    with patch("builtins.input", return_value=""):

        assert confirm_cleanup() is False
