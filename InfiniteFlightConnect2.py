from importlib.util import spec_from_file_location
from os import uname
import time
import struct
import socket
import json
import logging
from util import recieve, unpack

logger = logging.getLogger()
ch = logging.StreamHandler()
fh = logging.FileHandler('detail.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

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

        self.get_manifest()


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
        length = struct.unpack('<l', length)[0]
        logger.info('item: {}, length: {}'.format(item, length))
        
        recvd = 0
        response = bytes()
        while recvd < length:
            response += self.conn.recv(length - recvd)
            recvd = len(response)

     
        response = response[4:].decode('utf-8')
        logger.debug('{}'.format(response))
        
        entries = response.split('\n')
        self.manifest = {}
        for line in entries[:-1]:
            (id, data_type, id_name) = line.split(',')
            self.manifest[id_name] = {}
            self.manifest[id_name]['id'] = int(id)
            self.manifest[id_name]['data_type'] = int(data_type)

    
    def get_state(self, id, data_type):

        request = struct.pack('<lx', id)
        self.conn.sendall(request)

        response = recieve(self.conn, 4)
        return_id = unpack(response, data_type=1)
        response = recieve(self.conn, 4)
        return_length = unpack(response, data_type=1)
        logger.debug('return: id: {}, length: {}'.format(return_id, return_length))

        pay_load = recieve(self.conn, return_length)
        return_value = unpack(pay_load, data_type)
        logger.debug('{}'.format(return_value))

        return return_value


    def get_state_by_name(self, name):
        if name in self.manifest.keys():
            return self.get_state(self.manifest[name]['id'], self.manifest[name]['data_type'])
        else:
            return 'No such manifest item: {}'.format(name)

    def set_state(self, id, data_type, value):
        pass

    def set_state_with_check(self, id, data_type, value):
        pass


    def get_aircraft_state(self):
        state = {}
        
        state['Name'] = self.get_state_by_name('aircraft/0/name')
        state['AltitudeAGL'] = self.get_state_by_name('aircraft/0/altitude_agl')
        state['AltitudeMSL'] = self.get_state_by_name('aircraft/0/altitude_msl')
        state['GroundSpeed'] = self.get_state_by_name('aircraft/0/groundspeed')
        state['HeadingMagnetic'] = self.get_state_by_name('aircraft/0/heading_magnetic')
        state['HeadingTrue'] = self.get_state_by_name('aircraft/0/heading_true')
        state['VerticalSpeed'] = self.get_state_by_name('aircraft/0/vertical_speed')
        state['Location'] = {}
        state['Location']['Altitude'] = self.get_state_by_name('aircraft/0/altitude_msl')
        state['Location']['Latitude'] = self.get_state_by_name('aircraft/0/latitude')
        state['Location']['Longitude'] = self.get_state_by_name('aircraft/0/longitude')

        return state


    # close the socket
    def close(self):
        self.conn.close()



if __name__ == '__main__':
    ifc = IFClient()
    print(ifc.get_aircraft_state())
        
    ifc.close()

    #print(ifc.send_command("Airplane.GetState", [], await_response=True))