import InfiniteFlightConnect
import logging
logging.basicConfig(level=logging.DEBUG)

ifc = InfiniteFlightConnect.IFClient()
print(ifc.send_command("Airplane.GetState", [], await_response=True))