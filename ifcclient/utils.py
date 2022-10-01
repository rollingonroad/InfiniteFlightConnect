import struct
import math

from pkg_resources import to_filename
# convert byte array to specific DataType, raise exception if payload length mismatch with DataType
def unpack(payload, data_type):
    payload_length = len(payload)
    
    if data_type == 0 and payload_length == 1:
        return struct.unpack('?', payload)[0]
    if data_type == 1 and payload_length == 4:
        return struct.unpack('<l', payload)[0]
    if data_type == 2 and payload_length == 4:
        return struct.unpack('<f', payload)[0]
    if data_type == 3 and payload_length == 8:
        return struct.unpack('<d', payload)[0]
    if data_type == 4:
        # tricky one, only string has length, so skip four bytes.
        return payload[4:].decode('utf-8')
    if data_type == 5 and payload_length == 8:
        return struct.unpack('<q', payload)[0]
    else:
        raise TypeError('the length is not fit the data type')

# convert specific DataType to byte array, raise exception if value type mismatch with DataType
def pack(value, data_type):
    if data_type == 0 and isinstance(value, bool):
        return struct.pack('?', value)
    if data_type == 1 and isinstance(value, int):
        return struct.pack('<l', value)
    if data_type == 2 and isinstance(value, float):
        return struct.pack('<f', value)
    if data_type == 3 and isinstance(value, float):
        return struct.pack('<d', value)
    if data_type == 4 and isinstance(value, str):
        return struct.pack('<l', len(value)) + value.encode('utf-8')
    if data_type == 5 and isinstance(value, int):
        return struct.pack('<q', value)
    else:
        raise TypeError('value is not match with data type')

# recieve specific size from the socket
def recieve(conn, size):
    recved = 0
    buf = bytes()
    while recved < size:
        buf += conn.recv(size - recved)
        recved = len(buf)
    return buf

# convert rad to ang
def rad_to_ang(rad):
    return rad * 180 / math.pi

# convert speed m/s to knot/h
def mps_to_kph(mps):
    return mps * 3.6 * 0.539956803

# convert vertical speed, m/s to feet/min
def mps_to_fpm(mps):
    return mps * 60 * 3.2808399