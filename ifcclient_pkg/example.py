import InfiniteFlightConnect
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


ifc = InfiniteFlightConnect.IFClient()
print(ifc.send_command("Airplane.GetState", [], await_response=True))