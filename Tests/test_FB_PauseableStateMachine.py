"""Tests for FB_StateMachine"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from time import sleep

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_PAUSEABLESTATEMACHINE"
    PREFIX_FB = "PRG_TEST_FB_PAUSEABLESTATEMACHINE.fbStateMachine"

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
        self.PAUSE_STATE = conn.read_by_name(f"{self.PREFIX}.PAUSE_STATE")
        return super().setUp()

    def pause(self) -> None:
        conn.write_by_name(f"{self.PREFIX_FB}.bRequestPause", True)
        conn.write_by_name(f"{self.PREFIX}.bDoSomething", True)
        wait_cycles(1)

    def test_pause(self) -> None:
        self.pause()
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.nState"), self.PAUSE_STATE)

    def test_ignore_pause(self) -> None:
        conn.write_by_name(f"{self.PREFIX_FB}.bIgnorePause", True)
        conn.write_by_name(f"{self.PREFIX_FB}.bRequestPause", True)
        conn.write_by_name(f"{self.PREFIX}.bDoSomething", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.nState"), 1)
        self.assertFalse(conn.read_by_name(f"{self.PREFIX_FB}.bIgnorePause"))

    def test_resume(self) -> None:
        self.pause()
        conn.write_by_name(f"{self.PREFIX_FB}.bRequestPause", False)
        conn.write_by_name(f"{self.PREFIX}.bDoSomething", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.nState"), 1)


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
