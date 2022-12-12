"""Tests for conversion functions"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from datetime import datetime

import pyads

from connection import cold_reset, conn, wait_value

COLD_RESET = False


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_CONVERSION"

    @classmethod
    def setUpClass(cls) -> None:
        conn.open()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        conn.close()

    def setUp(self) -> None:
        if COLD_RESET:
            cold_reset()
        conn.write_by_name(f"{self.PREFIX}.bEnableTests", True)
        return super().setUp()

    def test_dt_to_str(self):
        # Value 1 equals 1 seconds after epoch
        conn.write_by_name(f"{self.PREFIX}.in_dt", 1, pyads.PLCTYPE_DT)
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.out_str"),
            "1970-01-01 00:00:01",
        )

    def test_dt_to_str_empty(self):
        """return empty string if DT is 0 (epoch)"""
        conn.write_by_name(f"{self.PREFIX}.in_dt", 0, pyads.PLCTYPE_DT)
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.out_str"),
            "",
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
