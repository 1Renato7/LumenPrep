"""Smoke tests for the shared Python environment."""

from __future__ import annotations

import sys
import unittest


class EnvironmentTest(unittest.TestCase):
    def test_runtime_is_python_3_14_4(self) -> None:
        self.assertEqual(sys.version_info[:3], (3, 14, 4))

    def test_application_package_is_importable(self) -> None:
        import app

        self.assertIsNotNone(app)
