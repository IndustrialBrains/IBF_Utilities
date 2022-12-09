"""Tests for FB_Base"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest

import pyads

from connection import cold_reset, conn, wait_cycles

COLD_RESET = True


class TestFB_Base(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_BASE"

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

    def test_fault(self):
        stFault = f"{self.PREFIX}.fbBase.stFault"
        conn.write_by_name(f"{stFault}.FaultType", 1, pyads.PLCTYPE_UDINT)
        conn.write_by_name(f"{stFault}.Description", "foobar")
        conn.write_by_name(f"{stFault}.Active", True)
        wait_cycles(1)
        self.assertEqual(
            conn.read_by_name("GVL_Utilities.fbFaultHandler.nActiveFaults"), 1
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
