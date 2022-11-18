"""
Tests for FB_ParameterHandler
"""
import sys
import unittest

# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import uuid
from random import random

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_PARAMETERHANDLER"

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

    def test_initial_state(self):
        # ParameterHandler always holds 1 dummy parameter ID
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.fbParameterHandler.nNumberOfParameters"),
            1,
        )
        self.assertEqual(
            conn.read_by_name(
                f"{self.PREFIX}.fbParameterHandler.arParameters[1].sName"
            ),
            conn.read_by_name(f"{self.PREFIX}.stParameterId.sName"),
        )

    def test_persistent(self):
        # Arrange
        EXPECTED_VALUE = str(uuid.uuid4())
        conn.write_by_name(f"{self.PREFIX}.stParameter.sName", EXPECTED_VALUE)

        # Act
        cold_reset()

        # Assert
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.sName"),
            EXPECTED_VALUE,
        )

    def test_add_parameter(self):
        # Arrange
        EXPECTED_VALUE = str(uuid.uuid4())
        conn.write_by_name(f"{self.PREFIX}.stParameter.sName", EXPECTED_VALUE)

        # Act
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)

        # Assert
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.fbParameterHandler.nNumberOfParameters"),
            1,
        )
        self.assertEqual(
            conn.read_by_name(
                f"{self.PREFIX}.fbParameterHandler.arParameters[1].sName"
            ),
            EXPECTED_VALUE,
        )

    def test_load_factory_value(self):
        # Arrange
        EXPECTED_VALUE = random()
        conn.write_by_name(f"{self.PREFIX}.stParameter.fFactory", EXPECTED_VALUE)

        # Act
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)
        wait_cycles(1)
        conn.write_by_name(f"{self.PREFIX}.fbParameterHandler.bCmdLoadfactory", True)

        # Assert
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.fValue"),
            EXPECTED_VALUE,
        )

    def test_load_teached_value(self):
        # Arrange
        EXPECTED_VALUE = random()
        conn.write_by_name(f"{self.PREFIX}.stParameter.fPrepared", EXPECTED_VALUE)

        # Act
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)
        wait_cycles(1)
        conn.write_by_name(f"{self.PREFIX}.fbParameterHandler.bCmdAcceptTeach", True)

        # Assert
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.fValue"),
            EXPECTED_VALUE,
        )

    def test_load_previous_value(self):
        # Arrange
        EXPECTED_VALUE = random()
        conn.write_by_name(f"{self.PREFIX}.stParameter.fSaved", EXPECTED_VALUE)

        # Act
        conn.write_by_name(f"{self.PREFIX}.bAddParameter", True)
        wait_cycles(1)
        conn.write_by_name(
            f"{self.PREFIX}.fbParameterHandler.bCmdLoadFromPrevious", True
        )

        # Assert
        self.assertEqual(
            conn.read_by_name(f"{self.PREFIX}.stParameter.fValue"),
            EXPECTED_VALUE,
        )


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
