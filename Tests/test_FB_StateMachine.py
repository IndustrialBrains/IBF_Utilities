"""Tests for FB_StateMachine"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from time import sleep

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_STATEMACHINE"

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

    def test_initial_state(self) -> None:
        self.assertEqual(conn.read_by_name(f"{self.PREFIX}.nState"), 0)
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.bStateChanged"))
        wait_cycles(2)
        self.assertGreater(conn.read_by_name(f"{self.PREFIX}.nTimeInState"), 0)

    def test_state_changed(self) -> None:
        conn.write_by_name(f"{self.PREFIX}.nState", 1)
        self.assertTrue(wait_value(f"{self.PREFIX}.bStateChanged", True, 0.1))
        conn.write_by_name(f"{self.PREFIX}.bStateChanged", False)
        wait_cycles(1)
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.bStateChanged"))

    def test_time_in_state(self) -> None:
        EXPECTED_VALUE = 500  # msec
        sleep(EXPECTED_VALUE / 1000)
        time_in_state_ms = conn.read_by_name(f"{self.PREFIX}.nTimeInState")
        margin_ms = 250
        self.assertTrue(
            margin_ms < time_in_state_ms < (EXPECTED_VALUE + margin_ms),
            f"time_in_state = {time_in_state_ms}",
        )
        # Reset time in state
        conn.write_by_name(f"{self.PREFIX}.nState", 1)
        wait_cycles(1)
        self.assertLess(conn.read_by_name(f"{self.PREFIX}.nTimeInState"), margin_ms)


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
