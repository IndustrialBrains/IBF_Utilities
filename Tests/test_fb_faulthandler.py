"""Tests for FB_FaultHandler"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from enum import IntEnum

import pyads

from connection import cold_reset, conn, wait_cycles

COLD_RESET = True


class E_FaultTypes(IntEnum):
    NA = 0  # Not applicable
    OM = 1  # Operator message
    MC = 2  # Missing condition
    CF = 3  # Cycle Fault
    FF = 4  # Fatal fault
    OW = 5  # Operator warning


class TestFB_FaultHandler(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_FAULTHANDLER"

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

    def activate_fault(self, fault_type: E_FaultTypes, description: str):
        conn.write_by_name(
            f"{self.PREFIX}.stFault.FaultType", fault_type, pyads.PLCTYPE_UDINT
        )
        conn.write_by_name(f"{self.PREFIX}.stFault.Description", description)
        # Always set Active TRUE as last, because it clear stFault
        conn.write_by_name(f"{self.PREFIX}.stFault.Active", True)
        wait_cycles(1)

    def test_00_initial_state(self):
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.fbFaultHandler.nActiveFaults"), 0
        )

    def test_add_fault(self):
        """Add a fault of each type, and check if the asociated bActXXX BOOLs are set"""
        fault_outputs = [
            "",  # Fault type NA doesn't have a BOOL
            "bActOM",
            "bActMC",
            "bActCF",
            "bActFF",
            "bActOW",
        ]
        for faulttype in E_FaultTypes:
            if faulttype == E_FaultTypes.NA:
                continue
            with self.subTest(faulttype.name):
                # description must be unique, otherwise the fault is ignored
                self.activate_fault(faulttype, f"fault of type {faulttype.name}")
                self.assertEqual(
                    conn.read_by_name(
                        f"{self.PREFIX}.fbFaultHandler.{fault_outputs[faulttype]}"
                    ),
                    True,
                )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
