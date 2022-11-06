import struct
import crc

crc_calculator = crc.CrcCalculator(crc.Crc16.CCITT)

# Use for bitflags
PACKET_TYPE_ARM_STATUS = 1
PACKET_TYPE_ALTITUDE = 2
PACKET_TYPE_ACCELERATION = 4
PACKET_TYPE_GPS_COORDINATES = 8
PACKET_TYPE_BOARD_TEMPERATURE = 16
PACKET_TYPE_BOARD_VOLTAGE = 32
PACKET_TYPE_BOARD_CURRENT = 64
PACKET_TYPE_BATTERY_VOLTAGE = 128
PACKET_TYPE_MAGNETOMETER = 256
PACKET_TYPE_GYROSCOPE = 512
PACKET_TYPE_GPS_SATELLITES = 1024
PACKET_TYPE_GPS_GROUND_SPEED = 2048

PAYLOAD_SIZE = {
    PACKET_TYPE_ARM_STATUS: 3,
    PACKET_TYPE_ALTITUDE: 8,
    PACKET_TYPE_ACCELERATION: 12,
    PACKET_TYPE_GPS_COORDINATES: 8,
    PACKET_TYPE_BOARD_TEMPERATURE: 16,
    PACKET_TYPE_BOARD_VOLTAGE: 16,
    PACKET_TYPE_BOARD_CURRENT: 16,
    PACKET_TYPE_BATTERY_VOLTAGE: 12,
    PACKET_TYPE_MAGNETOMETER: 12,
    PACKET_TYPE_GYROSCOPE: 12,
    PACKET_TYPE_GPS_SATELLITES: 2,
    PACKET_TYPE_GPS_GROUND_SPEED: 4
}

PAYLOAD_FORMAT = {
    PACKET_TYPE_ARM_STATUS: ">???",
    PACKET_TYPE_ALTITUDE: '>ff',
    PACKET_TYPE_ACCELERATION: '>fff',
    PACKET_TYPE_GPS_COORDINATES: '>ff',
    PACKET_TYPE_BOARD_TEMPERATURE: '>ffff',
    PACKET_TYPE_BOARD_VOLTAGE: '>ffff',
    PACKET_TYPE_BOARD_CURRENT: '>ffff',
    PACKET_TYPE_BATTERY_VOLTAGE: '>fff',
    PACKET_TYPE_MAGNETOMETER: '>fff',
    PACKET_TYPE_GYROSCOPE: '>fff',
    PACKET_TYPE_GPS_SATELLITES: '>h',
    PACKET_TYPE_GPS_GROUND_SPEED: '>f'
}

# Splits a packet type bitflag into multiple packet types.
# Code from <https://www.spatialtimes.com/2014/07/binary-flags-with-python/>
def get_packet_types(n):
    while n:
        b = n & (~n+1)
        yield b
        n ^= b

def create_packet(types: int, time: float, data: tuple) -> bytes:
    header = struct.pack('>hf', types, time)
    # footer = struct.pack('>h', checksum)

    body = bytes()
    type_flags: list[int] = get_packet_types(types)
    idx_data = 0
    for type_flag in type_flags:
        if type_flag == PACKET_TYPE_ARM_STATUS:
            body = body + struct.pack('>???', data[idx_data], data[idx_data + 1], data[idx_data + 2])
            idx_data += 3

        elif type_flag == PACKET_TYPE_ALTITUDE:
            body = body + struct.pack('>ff', data[idx_data], data[idx_data + 1])
            idx_data += 2

        elif type_flag == PACKET_TYPE_ACCELERATION:
            body = body + struct.pack('>fff', data[idx_data], data[idx_data + 1], data[idx_data + 2])
            idx_data += 3
        
        elif type_flag == PACKET_TYPE_GPS_COORDINATES:
            body = body + struct.pack('>ff', data[idx_data], data[idx_data + 1])
            idx_data += 2
        
        elif type_flag == PACKET_TYPE_BOARD_TEMPERATURE:
            body = body + struct.pack('>ffff', data[idx_data], data[idx_data + 1], data[idx_data + 2], data[idx_data + 3])
            idx_data += 4

        elif type_flag == PACKET_TYPE_BOARD_VOLTAGE:
            body = body + struct.pack('>ffff', data[idx_data], data[idx_data + 1], data[idx_data + 2], data[idx_data + 3])
            idx_data += 4

        elif type_flag == PACKET_TYPE_BOARD_CURRENT:
            body = body + struct.pack('>ffff', data[idx_data], data[idx_data + 1], data[idx_data + 2], data[idx_data + 3])
            idx_data += 4

        elif type_flag == PACKET_TYPE_BATTERY_VOLTAGE:
            body = body + struct.pack('>fff', data[idx_data], data[idx_data + 1], data[idx_data + 2])
            idx_data += 3

        elif type_flag == PACKET_TYPE_MAGNETOMETER:
            body = body + struct.pack('>fff', data[idx_data], data[idx_data + 1], data[idx_data + 2])
            idx_data += 3

        elif type_flag == PACKET_TYPE_GYROSCOPE:
            body = body + struct.pack('>fff', data[idx_data], data[idx_data + 1], data[idx_data + 2])
            idx_data += 3

        elif type_flag == PACKET_TYPE_GPS_SATELLITES:
            body = body + struct.pack('>h', data[idx_data])
            idx_data += 1

        elif type_flag == PACKET_TYPE_GPS_GROUND_SPEED:
            body = body + struct.pack('>f', data[idx_data])
            idx_data += 1
    
    checksum = crc_calculator.calculate_checksum(header + body)
    footer = struct.pack('>i', checksum)

    return header + body + footer
