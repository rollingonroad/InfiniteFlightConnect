import time
import struct
import socket
import json
import logging

logger = logging.getLogger()
ch = logging.StreamHandler()
fh = logging.FileHandler('detail.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)
logger.setLevel(logging.ERROR)

class IFClient(object):
    def __init__(self) -> None:
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("", 15000))
        while True:
            (data, addr) = udp.recvfrom(4096)
            if data:
                logger.info('Got broadcast udp packet, from: {}'.format(addr[0]))
                logger.debug('Content:\n{}'.format(json.dumps(json.loads(data.decode('utf-8')), indent=4)))
                break
        udp.close()

        self.device_ip = addr[0]
        self.device_port = 10112
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
    
    def get_manifest(self):
        request = struct.pack('<lx', -1)
        self.conn.sendall(request)
        item = self.conn.recv(4)
        length = self.conn.recv(4)
        #(item, length) = struct.unpack('<ll', header)
        length = struct.unpack('<l', length)[0]
        logger.info('item: {}, length: {}'.format(item, length))
        
        recvd = 0
        response = bytes()
        while recvd < length:
            response += self.conn.recv(length - recvd)
            recvd = len(response)

     
        response = response[4:].decode('utf-8')
        entries = response.split('\n')
        logger.debug('{}'.format(response))

        #logger.debug('{}'.format(entries))
    
    def get_state(self, id):
        request = struct.pack('<lx', id)
        logger.debug('{}'.format(request))
        self.conn.sendall(request)
        response = self.conn.recv(4)
        logger.debug('{}'.format(response))
        return_id = struct.unpack('<l', response)[0]
        response = self.conn.recv(4)
        return_length = struct.unpack('<l', response)[0]
        recved = 0
        response = bytes()
        while recved < return_length:
            response += self.conn.recv(return_length - recved)
            recved = len(response)
        
        pay_load = response[4:]
        lat = struct.unpack('<f', pay_load)[0]
        logger.debug('{}'.format(lat))

        return lat


    
    def close(self):
        self.conn.close()



if __name__ == '__main__':
    ifc = IFClient()
    ifc.get_manifest()
    for i in range(500):
        lat = ifc.get_state(628)
        print('current lat: {}'.format(lat))
        time.sleep(10)

    ifc.close()

    #print(ifc.send_command("Airplane.GetState", [], await_response=True))