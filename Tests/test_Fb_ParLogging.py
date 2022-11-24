"""
Tests for Fb_ParLogging

TODO: Page faults can be triggered, currently suppressed by null pointer
      checks in CmdParLoadFromFile and CmdParWriteFromFile

TODO: test weird strings
TODO: test long strings >255 character CSV line in total
TODO: test extreme float values 
TODO: test always init, never block
TODO: test corrupt csv file
TODO: test mismatch number of parameters
TODO: test mismatch number of columns
TODO: test parameters added in different order
"""
import sys
import unittest

# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import uuid
from random import random
from time import sleep

import pyads

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    # /tmp/parameters.csv

    PREFIX = "PRG_TEST_FB_PARLOGGING"

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
        return super().setUp()

    def test_write_to_file(self):
        FILENAME = f"/tmp/{self.PREFIX}_{uuid.uuid4()}.csv"

        # Add a parameter with a random factory value
        PARAMETER_NUMBER = int(10000 * random())
        EXPECTED_VALUE = random()
        conn.write_by_name(f"{self.PREFIX}.stParameter.nNumber", PARAMETER_NUMBER)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sName", str(uuid.uuid4()))
        conn.write_by_name(f"{self.PREFIX}.stParameter.fFactory", EXPECTED_VALUE)
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)

        # Set file path
        conn.write_by_name(
            "GVL_Parameters.sPARLIST_FILE", FILENAME, pyads.PLCTYPE_STRING
        )

        # Save to file by triggering Init
        conn.write_by_name(f"{self.PREFIX}.bInit", True)
        wait_cycles(50)

        # Wait for successful write
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 1))

        # Change factory value
        conn.write_by_name(f"{self.PREFIX}.stParameter.fFactory", random())

        # Reload by cold reset + Init
        cold_reset()
        conn.write_by_name(
            "GVL_Parameters.sPARLIST_FILE", FILENAME, pyads.PLCTYPE_STRING
        )
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)
        conn.write_by_name(f"{self.PREFIX}.bInit", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 1))

        # Validate factory value was reloaded
        self.assertAlmostEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.fFactory"),
            EXPECTED_VALUE,
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
