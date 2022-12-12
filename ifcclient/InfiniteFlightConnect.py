import time
import struct
import socket
import json
import logging
from abc import ABCMeta, abstractmethod

from .utils import recieve, unpack, rad_to_ang, mps_to_kph, mps_to_fpm, pack

logger = logging.getLogger()
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARN)

class IFCClient(object):
    """Factory class to get Infinite Flight Connect API client object
    """
    @staticmethod
    def discover_devices(duration=30):
        """discover devices in the same network
            a static method, to discover devices ip which running Infinite Flight Simulator in the same network
            in specific duration.
        :param duration: how many seconds we listen for udp broadcast packet. default 30 seconds. if duration=0, 
            return when we receive frist udp broadcast packet.
        :return: An ip list
        :rtype: list
        """
        devices = []
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("", 15000))

        old_timeout = udp.gettimeout()
        if duration == 0:
            deadline = time.time() + 120
        else:
            deadline = time.time() + duration
        while time.time() < deadline:
            udp.settimeout(deadline - time.time())
            try:
                (data, addr) = udp.recvfrom(4096)
                if data:
                    logger.info('Got broadcast udp packet, from: %s', addr[0])
                    logger.debug('Content:\n %s',json.dumps(json.loads(data.decode('utf-8')), indent=4))
                    device_ip = addr[0]
                    if device_ip not in devices:
                        devices.append(device_ip)
                    if duration == 0:
                        return devices
            except socket.timeout:
                pass

        udp.settimeout(old_timeout)
        udp.close()

        return devices

    @staticmethod
    def connect(ip, version=2):
        """Connect to device
        """
        if version == 1:
            return APIClientV1(ip)
        else:
            return APIClientV2(ip)

class APIClient(metaclass=ABCMeta):
    """Base class for APIClient.
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_aircraft_state(self):
        """get aircraft state
        """
        raise NotImplementedError

    @abstractmethod
    def get_flightplan(self):
        """get flight plan
        """
        raise NotImplementedError

    @abstractmethod
    def display_commands(self):
        """list all avaliable command
        """
        raise NotImplementedError

    def close(self):
        self.conn.close()

class APIClientV1(APIClient):
    """Api client version 1
    """
    def __init__(self, ip):
        """Used to prepare the socket connection to Infinite Flight device, and init the
            commandlist.
        :param ip: Infinite Flight device ip.
        """
        super().__init__()
        self.version = 1
        self.device_ip = ip
        self.device_port = 10111

        self.device_addr = (self.device_ip, self.device_port)

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.device_addr)
        
        self.get_listcommands()
        
    def send_command(self, cmd, params, await_response=False):
        """Send command to API v1, and recieve response.
            Send command to Infinite Flight Connect API version 1
            :param cmd: command to send
            :param params: list of parameter to send
            :await_response: by default False, return immediatly after send the command, if set True,
                receive response.
            :return: response string
            :rtype: str
        """
        request = {"Command":cmd,"Parameters":params}
        request = json.dumps(request).encode("utf-8")
        request = struct.pack('<Hxx', len(request)) + request

        self.conn.sendall(request)

        if await_response:
            response_length = recieve(self.conn, 4)[:2]
            response_length = struct.unpack('<H', response_length)[0]
            
            response = recieve(self.conn, response_length)
            response = response.decode("utf-8")

            return response
        return None   

    def get_listcommands(self):
        """Built command list dict.
            Send command 'listcommnds' and recieve the response and parse to a dict.
        """
        response = self.send_command('listcommands', params=[], await_response=True)
        parsed = json.loads(response)
        self.commandlist = {}
        entries = parsed['Text'].strip().split('\n')
        for item in entries[1:]:
            command, descrition = item.split(':')
            self.commandlist[command] = descrition.strip()

    def get_aircraft_state(self):
        """Get the aircraft state.
            In V1, there is a simple command: airplane.getsate to get the
            aircraft state
        """
        state = self.send_command("airplane.getstate", [], await_response=True)
        state = json.loads(state)
        return state               
    
    def get_flightplan(self):
        """Get flightplan
        """
        flightplan = self.send_command("flightplan.get", [], await_response=True)
        return json.loads(flightplan)
    
    def display_commands(self):
        """List all avaliable command.
        """
        if self.version == 1:
            print(f"{'Command':<40}: {'Description':<40}")
            for command, description in self.commandlist.items():
                print(f'{command:<40}: {description:<40}')

class APIClientV2(APIClient):
    """Api client version 2
    """
    def __init__(self, ip):
        """Used to prepare the socket connection to Infinite Flight device, and init the
            manifest.
        :param ip: Infinite Flight device ip
        """
        super().__init__()
        self.version = 2
        self.device_ip = ip
        self.device_port = 10112
        self.device_addr = (self.device_ip, self.device_port)

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.device_addr)

        self.get_manifest()

    def get_manifest(self):
        """Build the manifest dict.
            Create the get manifest request, recieve response and parse to dictionary. 
        """
        request = struct.pack('<lx', -1)
        self.conn.sendall(request)
        item = self.conn.recv(4)
        length = self.conn.recv(4)
        length = struct.unpack('<l', length)[0]
        logger.debug('item: %s, length: %d', item, length)
        
        recvd = 0
        response = bytes()
        while recvd < length:
            response += self.conn.recv(length - recvd)
            recvd = len(response)

        response = response[4:].decode('utf-8').strip()
        logger.debug('%s', response)
        
        entries = response.split('\n')
        self.manifest = {}
        for line in entries:
            (state_id, data_type, id_name) = line.split(',')
            self.manifest[id_name] = {}
            self.manifest[id_name]['id'] = int(state_id)
            self.manifest[id_name]['data_type'] = int(data_type)
    
    def get_state(self, state_id, data_type):
        request = struct.pack('<lx', state_id)
        self.conn.sendall(request)

        response = recieve(self.conn, 4)
        return_id = unpack(response, data_type=1)
        response = recieve(self.conn, 4)
        return_length = unpack(response, data_type=1)
        logger.debug('return: id: %d, length: %d', return_id, return_length)

        pay_load = recieve(self.conn, return_length)
        value = unpack(pay_load, data_type)
        logger.debug('payload: %s', value)

        return value


    def get_state_by_name(self, name):
        """Implement API V2 GetState
            Send a get state reqeust and get the value from Infinite Flight Connect API V2.
            :param name: the state name.
            :return: the value of the command name. it will be: bool, int, str, float
            :rtype: bool, int, str, float
        """
        if name in self.manifest:
            return self.get_state(self.manifest[name]['id'], self.manifest[name]['data_type'])
        else:
            raise AttributeError("State name can't be found in manifest.")

    def set_state(self, state_id, data_type, value):
        request = bytes()
        if data_type in [0, 1, 2, 3, 4, 5]:
            request = pack(state_id, 1) + pack(True, 0) + pack(value, data_type)
        else:
            pass
        logger.debug('request: %s', request)
        self.conn.sendall(request)
        
    def set_state_by_name(self, name, value):
        """Implement API V2 SetState
            Send a set state request to assign new value to them.
            :param name: the state name.
            :param value: the value you want to set.
        """
        if name in self.manifest:
            state_id = self.manifest[name]['id']
            data_type = self.manifest[name]['data_type']
            logger.debug('id: %d, data_type: %d, value: %s', state_id, data_type, value)
            return self.set_state(state_id, data_type, value)
        else:
            raise AttributeError("State name can't be found in manifest.")

    def run_command(self, command_id):
        request = bytes()
        request = pack(command_id, 1) + pack(False, 0)
        logger.debug('request: %s', request)
        self.conn.sendall(request)
    
    def run_command_by_name(self, command):
        """To execute a command throught the API V2.
            Send a RunCommand request and execute the command in the device.
            :param command: the command to execute.
        """
        if command in self.manifest:
            command_id = self.manifest[command]['id']
            data_type = self.manifest[command]['data_type']
            if data_type != -1:
                return "It's state, you should use set_state_by_name() and provide a value."
            logger.debug('id: %d, data_type: %d', command_id, data_type)
            return self.run_command(command_id)
        else:
            raise AttributeError("command can't be found in manifest.")


    def get_aircraft_state(self):
        """Get the aircraft state
            in V2, need use many GetState queries and convert
            to right unit, for example, headingTrue need convert radian to
            angle.
        """
        state = {}
        state['Name'] = self.get_state_by_name('aircraft/0/name')
        state['AltitudeAGL'] = self.get_state_by_name('aircraft/0/altitude_agl')
        state['AltitudeMSL'] = self.get_state_by_name('aircraft/0/altitude_msl')

        state['IndicatedAirspeedKts'] = mps_to_kph(self.get_state_by_name('aircraft/0/indicated_airspeed'))
        state['GroundSpeedKts'] = mps_to_kph(self.get_state_by_name('aircraft/0/groundspeed'))

        state['HeadingMagnetic'] = rad_to_ang(self.get_state_by_name('aircraft/0/heading_magnetic'))
        state['HeadingTrue'] = rad_to_ang(self.get_state_by_name('aircraft/0/heading_true'))
        state['VerticalSpeed'] = mps_to_fpm(self.get_state_by_name('aircraft/0/vertical_speed'))
        state['Location'] = {}
        state['Location']['Altitude'] = self.get_state_by_name('aircraft/0/altitude_msl')
        state['Location']['Latitude'] = self.get_state_by_name('aircraft/0/latitude')
        state['Location']['Longitude'] = self.get_state_by_name('aircraft/0/longitude')
        return state

    def get_flightplan(self):
        """Get flightplan
        """
        name = 'aircraft/0/flightplan/full_info'
        flightplan = self.get_state_by_name(name)
        return json.loads(flightplan)

    def display_commands(self):
        """List all avaliable command.
        """
        print(f"{'Command':<68}{'ID':<8}{'DataType':<4}")
        for command, detail in self.manifest.items():
            command_id = detail['id']
            if command_id < 10000:
                data_type = detail['data_type']
            else:
                data_type = ''
            print(f'{command:<68}{command_id:<8}{data_type:<4}')

    def fill_manifest(self):
        for  command, detail in self.manifest.items():
            if detail['data_type'] != -1:
                command_id = detail['id']
                data_type = detail['data_type']
                value = self.get_state(command_id, data_type)
                detail['value'] = value
                detail['last_update'] = time.time()

    def dump_manifest(self):
        for command, detail in self.manifest.items():
            command_id = detail['id']
            data_type = detail['data_type']
            if 'value' in detail.keys() and command_id < 10000:
                value = detail['value']
                last_update = time.ctime(detail['last_update'])
                print(f'{command_id:<8}{data_type:<3}{value:<25}{command}')
            else:
                print(f'{command_id:<8}{data_type:<3}{command:<55}')