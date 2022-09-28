import InfiniteFlightConnect

ifc = InfiniteFlightConnect.IFClient()
print(ifc.send_command("Airplane.GetState", [], await_response=True))