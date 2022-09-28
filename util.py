import struct
# convert byte array to specific DataType, raise exception if payload length mismatch with DataType
def unpack(payload, data_type):
    payload_length = len(payload)
    
    if data_type == 0 and payload_length == 1:
            return_value = struct.unpack('?', payload)[0]
    elif data_type == 1 and payload_length == 4:
        return_value = struct.unpack('<l', payload)[0]
    elif data_type == 2 and payload_length == 4:
        return_value = struct.unpack('<f', payload)[0]
    elif data_type == 3 and payload_length == 8:
        return_value = struct.unpack('<d', payload)[0]
    elif data_type == 4:
        # tricky one, only string has length, so skip four bytes.
        return_value = payload[4:].decode('utf-8')
    elif data_type == 5 and payload_length == 8:
        return_value = struct.unpack('<q', payload)[0]
    else:
        # todo: raise exception
        pass

    return return_value

# recieve specific size from the socket
def recieve(conn, size):
    recved = 0
    buf = bytes()
    while recved < size:
        buf += conn.recv(size - recved)
        recved = len(buf)
    return buf
