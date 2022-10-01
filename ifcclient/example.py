import logging
import time

from InfiniteFlightConnect import IFCClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    ip_list = IFCClient.discover_devices(duration=15)
    ifc = IFCClient(ip_list[0])

    print(ifc.get_aircraft_state())

    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))
    ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
    time.sleep(3)
    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))

    ifc.run_command_by_name('commands/NextCamera')

    print(ifc.get_filghtplan())

    ifc.close()
