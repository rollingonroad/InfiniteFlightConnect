from ifcclient import IFCClient
import socket
import pytest
import json
import time

class TestVersion1:
    @pytest.mark.parametrize(
        "duration",
        (
            (0),
            (20),
            (30),
        )
    )
    def test_discover_device(self, duration):
        dev_list = IFCClient.discover_devices(duration)
        assert len(dev_list) > 0

    def test_init(self):
        dev_list = IFCClient.discover_devices(duration=0)
        ifc = IFCClient(dev_list[0], version=1)
        assert ifc.version == 1
        assert hasattr(ifc, 'commandlist')
        assert hasattr(ifc, 'conn')
        ifc = IFCClient(dev_list[0], version=2)
        assert ifc.version == 2
        assert hasattr(ifc, 'manifest')
        assert hasattr(ifc, 'conn')
        ifc.get_aircraft_state()
        state = ifc.get_aircraft_state()
        assert isinstance(state, dict)
        assert "GroundSpeedKts" in state.keys()
        flapstate = ifc.get_state_by_name('aircraft/0/systems/flaps/state')
        assert isinstance(flapstate, int)
        ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
        time.sleep(3)
        flapstate = ifc.get_state_by_name('aircraft/0/systems/flaps/state')
        assert flapstate == 2

    # ifc.run_command_by_name('commands/NextCamera')

    # print(ifc.get_filghtplan())
    # ifc.dsiplay_commands()

    # ifc.close()

    # # test version 1
    # ifc = ifcclient.IFCClient(ips[0], version=1)

    # print(ifc.get_aircraft_state())

    # print(ifc.get_filghtplan())

    # ifc.get_listcommands()
    # ifc.dsiplay_commands()

    # ifc.close()




