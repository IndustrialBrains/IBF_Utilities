"""Tests for FB_FaultHandler"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from enum import IntEnum, auto

import pyads

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class E_FaultTypes(IntEnum):
    OM = 0  # Operator message
    MC = auto()  # Missing condition
    CF = auto()  # Cycle Fault
    FF = auto()  # Fatal fault
    OW = auto()  # Operator warning


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
        conn.write_by_name(f"{self.PREFIX}.bEnableTests", True)
        return super().setUp()

    def _update_fault(
        self,
        faulttype: E_FaultTypes,
        description: str | None = None,
        active: bool = True,
    ):
        """(De)activate a fault by writing data to stFault"""
        conn.write_by_name(
            f"{self.PREFIX}.fbBase.stFault.FaultType", faulttype, pyads.PLCTYPE_UINT
        )
        if description:
            conn.write_by_name(f"{self.PREFIX}.fbBase.stFault.description", description)
        conn.write_by_name(f"{self.PREFIX}.fbBase.stFault.Active", active)

    def _check_active_fault_type(
        self, faulttype: E_FaultTypes, expected_status: bool
    ) -> None:
        """Check if a fault type is active (or not)"""
        self.assertEqual(
            wait_value(
                f"GVL_Utilities.fbFaultHandler.arActiveFaultTypes[{faulttype}]",
                expected_status,
                0.5,
            ),
            True,
        )

    def _trigger_reset(self):
        """Trigger CmdReset"""
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertEqual(
            wait_value(
                f"{self.PREFIX}.bCmdReset",
                False,
                0.5,
            ),
            True,
        )

    def test_00_initial_state(self):
        self.assertEqual(
            conn.read_by_name(f"GVL_Utilities.fbFaultHandler.nFaultsInLog"), 0
        )
        for faulttype in E_FaultTypes:
            self.assertFalse(
                conn.read_by_name(
                    f"GVL_Utilities.fbFaultHandler.arActiveFaultTypes[{faulttype}]"
                )
            )

    def test_01_add_fault(self):
        """Add a fault of each type, and check if the asociated fault type is reported"""
        # active_faults = 0
        for faulttype in E_FaultTypes:
            with self.subTest(faulttype.name):
                # description must be unique, otherwise the fault is ignored
                self._update_fault(faulttype)
                self._check_active_fault_type(faulttype, True)

    def test_02_reset_active_fault(self):
        faulttype = E_FaultTypes.OM
        self._update_fault(faulttype)
        self._check_active_fault_type(faulttype, True)
        self._trigger_reset()
        # Reset should have no effect (fault still active)
        self._check_active_fault_type(faulttype, True)

    def test_03_reset_inactive_fault(self):
        faulttype = E_FaultTypes.OM
        self._update_fault(faulttype)
        self._check_active_fault_type(faulttype, True)
        conn.write_by_name(f"{self.PREFIX}.fbBase.stFault.Active", False)
        self._trigger_reset()
        self._check_active_fault_type(faulttype, False)

    def test_04_add_to_log(self):
        for i in range(3):
            self._update_fault(E_FaultTypes.OM, description=str(i + 1))
            self.assertEqual(
                conn.read_by_name(f"GVL_Utilities.fbFaultHandler.nFaultsInLog"), i + 1
            )

    def test_05_count_active_faults(self):
        self._update_fault(E_FaultTypes.OM)
        self.assertEqual(
            conn.read_by_name(f"GVL_Utilities.fbFaultHandler.nActiveFaults"), 1
        )
        self._update_fault(E_FaultTypes.OM, active=False)
        self.assertEqual(
            conn.read_by_name(f"GVL_Utilities.fbFaultHandler.nActiveFaults"), 0
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
