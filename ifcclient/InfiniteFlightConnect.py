import time
import struct
import socket
import json
import logging
from ifcclient.utils import recieve, unpack, rad_to_ang, mps_to_kph, mps_to_fpm, pack

logger = logging.getLogger()
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARN)

#fh = logging.FileHandler('detail.log', mode='a')
#logger.addHandler(fh)
#logger.setLevel(logging.DEBUG)

class IFCClient(object):
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

        # close the client
    def close(self):
        self.conn.close()


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

     
        response = response[4:].decode('utf-8').strip()
        logger.debug('{}'.format(response))
        
        entries = response.split('\n')
        self.manifest = {}
        for line in entries:
            (id, data_type, id_name) = line.split(',')
            self.manifest[id_name] = {}
            self.manifest[id_name]['id'] = int(id)
            self.manifest[id_name]['data_type'] = int(data_type)
    
    def fill_manifest(self):
        for name in self.manifest.keys():
            if self.manifest[name]['data_type'] != -1:
                id = self.manifest[name]['id']
                data_type = self.manifest[name]['data_type']
                value = self.get_state(id, data_type)
                self.manifest[name]['value'] = value
                self.manifest[name]['last_update'] = time.time()

    def dump_manifest(self):
        for name in self.manifest.keys():
            id = self.manifest[name]['id']
            data_type = self.manifest[name]['data_type']
            if 'value' in self.manifest[name].keys() and id < 10000:
                value = self.manifest[name]['value']
                last_update = time.ctime(self.manifest[name]['last_update'])
                print('{:<8}{:<3}{:<25}{}'.format(id, data_type, value, name))
            else:
                print('{:<8}{:<3}{:<55}'.format(id, data_type, name))

    
    def get_state(self, id, data_type):

        request = struct.pack('<lx', id)
        self.conn.sendall(request)

        response = recieve(self.conn, 4)
        return_id = unpack(response, data_type=1)
        response = recieve(self.conn, 4)
        return_length = unpack(response, data_type=1)
        logger.debug('return: id: {}, length: {}'.format(return_id, return_length))

        pay_load = recieve(self.conn, return_length)
        value = unpack(pay_load, data_type)
        logger.debug('{}'.format(value))

        return value


    def get_state_by_name(self, name):
        if name in self.manifest.keys():
            return self.get_state(self.manifest[name]['id'], self.manifest[name]['data_type'])
        else:
            return 'No such manifest item: {}'.format(name)

    def set_state(self, id, data_type, value):
        request = bytes()
        if data_type in [0, 1, 2, 3, 4, 5]:
            request = pack(id, 1) + pack(True, 0) + pack(value, data_type)
        else:
            pass
        logger.debug('request: {}'.format(request))
        self.conn.sendall(request)
        
    def set_state_by_name(self, name, value):
        if name in self.manifest.keys():
            id = self.manifest[name]['id']
            data_type = self.manifest[name]['data_type']
            logger.debug('id: {}, data_type: {}, value: {}'.format(id, data_type, value))
            return self.set_state(id, data_type, value)
        else:
            pass

    def run_command(self, id):
        request = bytes()
        request = pack(id, 1) + pack(False, 0)
        logger.debug('request: {}'.format(request))
        self.conn.sendall(request)
    
    def run_command_by_name(self, command):
        if command in self.manifest.keys():
            id = self.manifest[command]['id']
            data_type = self.manifest[command]['data_type']
            if data_type != -1:
                return "It's state, you should use set_state_by_name() and provide a value."
            logger.debug('id: {}, data_type: {}'.format(id, data_type))
            return self.run_command(id)
        else:
            pass


    def get_aircraft_state(self):
        state = {}
        
        state['Name'] = self.get_state_by_name('aircraft/0/name')
        state['AltitudeAGL'] = self.get_state_by_name('aircraft/0/altitude_agl')
        state['AltitudeMSL'] = self.get_state_by_name('aircraft/0/altitude_msl')
        state['GroundSpeed'] = self.get_state_by_name('aircraft/0/groundspeed')
        state['GroundSpeedKts'] = mps_to_kph(state['GroundSpeed'])
        state['HeadingMagnetic'] = rad_to_ang(self.get_state_by_name('aircraft/0/heading_magnetic'))
        state['HeadingTrue'] = rad_to_ang(self.get_state_by_name('aircraft/0/heading_true'))
        state['VerticalSpeed'] = mps_to_fpm(self.get_state_by_name('aircraft/0/vertical_speed'))
        state['Location'] = {}
        state['Location']['Altitude'] = self.get_state_by_name('aircraft/0/altitude_msl')
        state['Location']['Latitude'] = self.get_state_by_name('aircraft/0/latitude')
        state['Location']['Longitude'] = self.get_state_by_name('aircraft/0/longitude')

        return state

    def get_filghtplan(self):
        name = 'aircraft/0/flightplan/full_info'
        flightplan = self.get_state_by_name(name)
        return json.loads(flightplan)


if __name__ == '__main__':
    ifc = IFCClient()

    print(ifc.get_aircraft_state())

    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))
    ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
    time.sleep(3)
    print(ifc.get_state_by_name('aircraft/0/systems/flaps/state'))

    ifc.run_command_by_name('commands/NextCamera')

    print(ifc.get_filghtplan())

    ifc.close()