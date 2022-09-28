import time
import struct
import socket
import json

class IFClient(object):
    def __init__(self) -> None:
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("", 15000))
        while True:
            (data, addr) = udp.recvfrom(4096)
            if data:
                break
        udp.close()

        self.device_ip = addr[0]
        self.device_port = 10111
        self.device_addr = (self.device_ip, self.device_port)

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.device_addr)

    def send_command(self, cmd, params, await_response=False):
        request = {"Command":cmd,"Parameters":params}
        request = json.dumps(request).encode("utf-8")
        request = struct.pack('<Hxx', len(request)) + request

        self.conn.sendall(request)

        if await_response:
            response_length = self.conn.recv(4)[:2]
            response_length = struct.unpack('<H', response_length)[0]
            
            # keep recv till reach the response_length
            recved = 0
            response = bytes()
            while recved < response_length:
                response += self.conn.recv(response_length - recved)
                recved = len(response)
            response = response.decode("utf-8")

            return response
        else:
            print(f"{self.device_addr} [REQUEST SENT SUCCESSFULLY to {self.device_ip} : {self.device_port}] Request sent to Infinite Flight successfully")
        return None