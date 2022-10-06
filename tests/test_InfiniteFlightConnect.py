import socket
import pytest
import json
import time
from ifcclient import IFCClient

class TestAPIClient:
    @pytest.mark.parametrize(
        "duration",
        (
            (0),
        )
    )
    def test_discover_device(self, duration):
        dev_list = IFCClient.discover_devices(duration)
        assert len(dev_list) > 0

    def test_version2(self, capfd):
        dev_list = IFCClient.discover_devices(0)
        assert len(dev_list) > 0
        ifc = IFCClient.connect(dev_list[0], version=2)
        assert ifc.version == 2
        assert hasattr(ifc, 'manifest')
        assert hasattr(ifc, 'conn')
        state = ifc.get_aircraft_state()
        assert isinstance(state, dict)
        assert "GroundSpeedKts" in state.keys()
        flapstate = ifc.get_state_by_name('aircraft/0/systems/flaps/state')
        assert isinstance(flapstate, int)
        ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
        time.sleep(3)
        flapstate = ifc.get_state_by_name('aircraft/0/systems/flaps/state')
        assert flapstate == 2

        ifc.run_command_by_name('commands/NextCamera')

        flightplan = ifc.get_flightplan()
        assert isinstance(flightplan, dict)
        assert len(flightplan) > 10

        ifc.display_commands()
        out, err = capfd.readouterr()
        assert 'NextCamera' in out
        ifc.close()

        
    def test_version1(self, capfd):
        dev_list = IFCClient.discover_devices(duration=0)
        assert len(dev_list) > 0
        ifc = IFCClient.connect(dev_list[0], version=1)
        assert ifc.version == 1
        assert hasattr(ifc, 'commandlist')
        assert hasattr(ifc, 'conn')
        state = ifc.get_aircraft_state()
        assert isinstance(state, dict)
        assert "GroundSpeedKts" in state.keys()
        flightplan = ifc.get_flightplan()
        assert isinstance(flightplan, dict)
        assert len(flightplan) > 10

        ifc.display_commands()
        out, err = capfd.readouterr()
        assert "airplane.getstate" in out

        ifc.close()




