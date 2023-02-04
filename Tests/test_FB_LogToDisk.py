"""Tests for FB_LogToDisk"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import math
import sys
import unittest
from time import sleep, time

import pyads

from connection import cold_reset, conn, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_LOGTODISK"
    PREFIX_FB = f"{PREFIX}.fbLogToDisk"

    MAX_ITEMS_IN_BUFFER = 0
    MAX_LOG_FILE_SIZE = 0

    @classmethod
    def setUpClass(cls) -> None:
        conn.open()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Stop to PLC to avoid filling the disk
        conn.write_control(pyads.ADSSTATE_STOP, 0, 0, pyads.PLCTYPE_BOOL)
        conn.close()

    def setUp(self) -> None:
        if COLD_RESET:
            cold_reset()

        # Get fbLogToDisk constants
        self.MAX_ITEMS_IN_BUFFER = conn.read_by_name(
            f"{self.PREFIX_FB}.MAX_ITEMS_IN_BUFFER"
        )
        self.MAX_LOG_FILE_SIZE = conn.read_by_name(f"{self.PREFIX_FB}.nMaxLogFileSize")

        conn.write_by_name(f"{self.PREFIX}.bEnableTests", True)
        return super().setUp()

    def test_write(self):
        """Write a log item"""
        # TODO: assert file is created and contents are as expected
        conn.write_by_name(f"{self.PREFIX}.bEnable", True)
        conn.write_by_name(f"{self.PREFIX}.sMsg", "Foobar", pyads.PLCTYPE_STRING)
        conn.write_by_name(f"{self.PREFIX}.bAddToLog", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bAddToLog", False, 0.1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX_FB}.bFault"))
        self.assertTrue(wait_value(f"{self.PREFIX_FB}.bLoggerInitialized", True, 1))

    def test_add_until_overflow(self):
        # NOTE: this only works if file write is disabled, otherwise
        # the buffer is emptied almost immediately by the file writer.
        for i in range(self.MAX_ITEMS_IN_BUFFER + 10):
            conn.write_by_name(f"{self.PREFIX}.sMsg", str(i + 1), pyads.PLCTYPE_STRING)
            conn.write_by_name(f"{self.PREFIX}.bAddToLog", True)
            self.assertTrue(wait_value(f"{self.PREFIX}.bAddToLog", False, 0.1))
            if conn.read_by_name(f"{self.PREFIX_FB}.bFault"):
                break
        self.assertTrue(i == self.MAX_ITEMS_IN_BUFFER)

    def test_add_until_file_size_reached(self):
        # NOTE: Assert manually!
        conn.write_by_name(f"{self.PREFIX}.bEnable", True)
        msg = "x" * 255
        for i in range(2 + math.ceil(self.MAX_LOG_FILE_SIZE / len(msg))):
            # show the counter value in the string to aid debugging
            msg = msg.replace(msg[0:6], f"{i:05.0f}-", 1)
            conn.write_by_name(f"{self.PREFIX}.sMsg", msg, pyads.PLCTYPE_STRING)
            conn.write_by_name(f"{self.PREFIX}.bAddToLog", True)
            self.assertTrue(wait_value(f"{self.PREFIX}.bAddToLog", False, 0.1))
            # wait at least one second to make sure the new file has a different filename
            sleep(1)

    def test_stress(self):
        # Flood the log with messages each PLC cycle, which should trigger
        # a buffer overflow and stop the logger
        conn.write_by_name(f"{self.PREFIX}.bEnable", True)
        conn.write_by_name(f"{self.PREFIX}.bStresstest", True)
        self.assertTrue(wait_value(f"{self.PREFIX_FB}.bFault", True, 5))


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
