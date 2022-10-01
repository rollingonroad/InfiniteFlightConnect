import logging
import time
import ifcclient


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    # test version 2
    ips = ifcclient.IFCClient.discover_devices(duration=0)
    print(ips)
    ifc = ifcclient.IFCClient(ips[0], version=2)

    print(ifc.get_aircraft_state())

    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))
    ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
    time.sleep(3)
    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))

    ifc.run_command_by_name('commands/NextCamera')

    print(ifc.get_filghtplan())
    ifc.dsiplay_commands()

    ifc.close()

    # test version 1
    ifc = ifcclient.IFCClient(ips[0], version=1)

    print(ifc.get_aircraft_state())

    print(ifc.get_filghtplan())

    ifc.get_listcommands()
    ifc.dsiplay_commands()

    ifc.close()