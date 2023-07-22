import unittest
from unittest import mock

from semver.utils import get_settings, setting_to_array
from semver.exceptions import SemverException


class TestUtils(unittest.TestCase):
    @mock.patch("toml.load")
    @mock.patch("pathlib.Path.is_file")
    def test_get_settings_toml(self, mock_is_file: mock.Mock, mock_toml: mock.Mock):
        get_settings.cache_clear()

        mock_is_file.side_effect = [True, False]

        mock_toml.return_value = {"1": {"a": "alpha", "fruit": "apple"}}
        settings = get_settings()
        self.assertEqual(settings, {"1": {"a": "alpha", "fruit": "apple"}})

    @mock.patch("configparser.ConfigParser")
    @mock.patch("pathlib.Path.is_file")
    def test_get_settings_cfg(
        self, mock_is_file: mock.Mock, mock_config_parser: mock.Mock
    ):
        get_settings.cache_clear()

        mock_is_file.side_effect = [False, True]

        mock_config_parser.return_value.read.return_value = ["./.bumpversion.cfg"]
        mock_config_parser.return_value.sections.return_value = ["1", "2", "3"]
        mock_config_parser.return_value.items.side_effect = [
            [("a", "alpha"), ("fruit", "apple")],
            [("b", "bravo"), ("fruit", "banana")],
            [("c", "charlie"), ("fruit", "cherry")],
        ]

        settings = get_settings()
        self.assertEqual(
            settings,
            {
                "1": {"a": "alpha", "fruit": "apple"},
                "2": {"b": "bravo", "fruit": "banana"},
                "3": {"c": "charlie", "fruit": "cherry"},
            },
        )

    @mock.patch("pathlib.Path.is_file")
    def test_get_settings_no_file(self, mock_is_file: mock.Mock):
        get_settings.cache_clear()

        mock_is_file.side_effect = [False, False]
        with self.assertRaises(SemverException):
            get_settings()

    @mock.patch("semver.utils.get_settings")
    def test_setting_to_array(self, mock_get_settings: mock.Mock):
        mock_get_settings.return_value = {"semver": {"test": "test1, test2"}}
        settings = setting_to_array("test")
        self.assertEqual(settings, ["test1", "test2"])
