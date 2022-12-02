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
import math
import sys
import unittest

# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import uuid

import pyads

from connection import cold_reset, conn, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    # /tmp/parameters.csv

    PREFIX = "PRG_TEST_FB_PARFILEHANDLER"

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

    def test_write_and_read(self):
        FILENAME = f"/tmp/{self.PREFIX}_{uuid.uuid4()}.csv"

        MIN_LREAL = (
            -1.7976931348623158e307
        )  # (almost) the minimal value of a LREAL, note that the actual minimum value `-1.7976931348623158e308` will crash the PLC (Beckhof bug)

        class ExpectedValues:
            nNumber = 0xFFFFFFFF
            sName = "n" * 50  # test will break if this goes above 58
            sType = "p" * 4
            sDiscription = "d" * 80
            fFactory = MIN_LREAL
            fMaximum = MIN_LREAL * 2
            fMinimum = MIN_LREAL * 3
            fValue = MIN_LREAL * 4
            sUnit = "u" * 8

        conn.write_by_name(f"{self.PREFIX}.stParameter.nNumber", ExpectedValues.nNumber)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sName", ExpectedValues.sName)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sType", ExpectedValues.sType)
        conn.write_by_name(
            f"{self.PREFIX}.stParameter.sDiscription", ExpectedValues.sDiscription
        )
        conn.write_by_name(
            f"{self.PREFIX}.stParameter.fFactory", ExpectedValues.fFactory
        )
        conn.write_by_name(
            f"{self.PREFIX}.stParameter.fMaximum", ExpectedValues.fMaximum
        )
        conn.write_by_name(
            f"{self.PREFIX}.stParameter.fMinimum", ExpectedValues.fMinimum
        )
        conn.write_by_name(f"{self.PREFIX}.stParameter.fValue", ExpectedValues.fValue)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sUnit", ExpectedValues.sUnit)
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)

        # Set file path
        conn.write_by_name(
            "GVL_Parameters.sPARLIST_FILE", FILENAME, pyads.PLCTYPE_STRING
        )

        # Save to file by triggering Init
        conn.write_by_name(f"{self.PREFIX}.bInit", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbParFileHandler.bError"))

        # Reset all values
        conn.write_by_name(f"{self.PREFIX}.stParameter.nNumber", 0)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sName", "")
        conn.write_by_name(f"{self.PREFIX}.stParameter.sType", "")
        conn.write_by_name(f"{self.PREFIX}.stParameter.sDiscription", "")
        conn.write_by_name(f"{self.PREFIX}.stParameter.fFactory", 0)
        conn.write_by_name(f"{self.PREFIX}.stParameter.fMaximum", 0)
        conn.write_by_name(f"{self.PREFIX}.stParameter.fMinimum", 0)
        conn.write_by_name(f"{self.PREFIX}.stParameter.fValue", 0)
        conn.write_by_name(f"{self.PREFIX}.stParameter.sUnit", "")

        # Reload by cold reset + Init
        cold_reset()
        conn.write_by_name(
            "GVL_Parameters.sPARLIST_FILE", FILENAME, pyads.PLCTYPE_STRING
        )
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)
        conn.write_by_name(f"{self.PREFIX}.bInit", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbParFileHandler.bError"))

        # Check results
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.nNumber"),
            ExpectedValues.nNumber,
        )
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.sName"),
            ExpectedValues.sName,
        )
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.sType"),
            ExpectedValues.sType,
        )
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.sDiscription"),
            ExpectedValues.sDiscription,
        )
        self.assertTrue(
            math.isclose(
                conn.read_by_name(f"{self.PREFIX}.stParameter.fFactory"),
                ExpectedValues.fFactory,
            )
        )
        self.assertTrue(
            math.isclose(
                conn.read_by_name(f"{self.PREFIX}.stParameter.fMaximum"),
                ExpectedValues.fMaximum,
            )
        )
        self.assertTrue(
            math.isclose(
                conn.read_by_name(f"{self.PREFIX}.stParameter.fMinimum"),
                ExpectedValues.fMinimum,
            )
        )
        self.assertTrue(
            math.isclose(
                conn.read_by_name(f"{self.PREFIX}.stParameter.fValue"),
                ExpectedValues.fValue,
            )
        )
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.sUnit"),
            ExpectedValues.sUnit,
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
