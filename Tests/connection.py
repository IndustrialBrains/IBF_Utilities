"""Provide a PyADS connection to a PLC"""
from time import sleep, time

import pyads

# conn = pyads.Connection("127.0.0.1.1.1", pyads.PORT_TC3PLC1)
# conn = pyads.Connection("192.168.178.25.1.1", pyads.PORT_TC3PLC1)
# conn = pyads.Connection("PC-975086", pyads.PORT_TC3PLC1)
conn = pyads.Connection("41.151.80.134.1.1", pyads.PORT_TC3PLC1)

ADS_COMMAND_DELAY = 0.020  # (sec) time to allow the PLC to handle ADS commands
PLC_CYCLETIME = 0.010  # (sec)


class TimeOutError(Exception):  # pylint: disable=missing-class-docstring
    ...


def cold_reset(timeout: float = 1.0):
    """Cold reset the PLC (similar to clicking the `Reset cold` button)"""
    conn.write_control(pyads.ADSSTATE_RESET, 0, 0, pyads.PLCTYPE_BOOL)
    conn.write_control(pyads.ADSSTATE_RUN, 0, 0, pyads.PLCTYPE_BOOL)

    start_time = time()
    while (time() - start_time) < timeout:
        (ads_state, _) = conn.read_state()
        if ads_state == pyads.ADSSTATE_RUN:
            return
        sleep(ADS_COMMAND_DELAY)

    raise TimeOutError(f"Cold reset failed (timeout after {timeout} seconds)")


def wait_cycles(cycles: int) -> None:
    """Wait for a number of PLC cycles. Cycletime is a fixed value: `PLC_CYCLETIME`"""
    sleep(PLC_CYCLETIME * cycles)
