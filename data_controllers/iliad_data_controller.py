from . import serial_data_controller
import serial
import struct
from utils import packet_util
import crc
import math

class IliadDataController(serial_data_controller.SerialDataController):

    def __init__(self) -> None:
        super().__init__()

        self.data_buffer = bytearray()
        self.checksum_calculator = crc.CrcCalculator(crc.Crc16.CCITT)

        self.arm_status_1_data: list[tuple[float, bool]] = []
        self.arm_status_2_data: list[tuple[float, bool]] = []
        self.arm_status_3_data: list[tuple[float, bool]] = []
        self.altitude_1_data: list[tuple[float, float]] = []
        self.altitude_2_data: list[tuple[float, float]] = []
        self.acceleration_x_data: list[tuple[float, float]] = []
        self.acceleration_y_data: list[tuple[float, float]] = []
        self.acceleration_z_data: list[tuple[float, float]] = []
        self.gps_latitude_data: list[tuple[float, float]] = []
        self.gps_longitude_data: list[tuple[float, float]] = []
        self.board_1_temperature_data: list[tuple[float, float]] = []
        self.board_2_temperature_data: list[tuple[float, float]] = []
        self.board_3_temperature_data: list[tuple[float, float]] = []
        self.board_4_temperature_data: list[tuple[float, float]] = []
        self.board_1_voltage_data: list[tuple[float, float]] = []
        self.board_2_voltage_data: list[tuple[float, float]] = []
        self.board_3_voltage_data: list[tuple[float, float]] = []
        self.board_4_voltage_data: list[tuple[float, float]] = []
        self.board_1_current_data: list[tuple[float, float]] = []
        self.board_2_current_data: list[tuple[float, float]] = []
        self.board_3_current_data: list[tuple[float, float]] = []
        self.battery_1_voltage_data: list[tuple[float, float]] = []
        self.battery_2_voltage_data: list[tuple[float, float]] = []
        self.battery_3_voltage_data: list[tuple[float, float]] = []
        self.magnetometer_data_1: list[tuple[float, float]] = []
        self.magnetometer_data_2: list[tuple[float, float]] = []
        self.magnetometer_data_3: list[tuple[float, float]] = []
        self.gyroscope_x_data: list[tuple[float, float]] = []
        self.gyroscope_y_data: list[tuple[float, float]] = []
        self.gyroscope_z_data: list[tuple[float, float]] = []
        self.gps_sattelites_data: list[tuple[float, int]] = []
        self.gps_ground_speed_data: list[tuple[float, float]] = []
    
    def update(self) -> None:
        if self.is_open():
            
            # Poll serial port and put anything there into data_buffer
            if self.port.in_waiting > 0:
                data = self.port.read_all()
                self.data_buffer += bytearray(data)
            
            # If the buffer has enough data, try to parse some of it
            if len(self.data_buffer) > 10:
                
                self.idx_cursor = 0 # Current index in data_buffer.

                packet_types_bytes: bytes
                packet_types: list[int] = []
                packet_timestamp_bytes: bytes
                packet_timestamp: float
                packet_payload_bytes = bytearray()
                packet_payload: dict[int] = {}
                packet_checksum_bytes: bytes
                packet_checksum: int

                # Parse header:
                if len(self.data_buffer) - self.idx_cursor >= 6:
                    packet_types_bytes = self.data_buffer[self.idx_cursor:(self.idx_cursor + 2)]
                    (packet_types_raw,) = struct.unpack('>h', packet_types_bytes)
                    packet_types: list[int] = list(packet_util.get_packet_types(packet_types_raw))
                    self.idx_cursor += 2
                    packet_timestamp_bytes = self.data_buffer[self.idx_cursor:(self.idx_cursor + 4)]
                    (packet_timestamp,) = struct.unpack('>f', packet_timestamp_bytes)
                    self.idx_cursor += 4
                
                for packet_type in [ # TODO: Turn constants into an enum.
                    packet_util.PACKET_TYPE_ARM_STATUS,
                    packet_util.PACKET_TYPE_ALTITUDE,
                    packet_util.PACKET_TYPE_ACCELERATION,
                    packet_util.PACKET_TYPE_GPS_COORDINATES,
                    packet_util.PACKET_TYPE_BOARD_TEMPERATURE,
                    packet_util.PACKET_TYPE_BOARD_VOLTAGE,
                    packet_util.PACKET_TYPE_BOARD_CURRENT,
                    packet_util.PACKET_TYPE_BATTERY_VOLTAGE,
                    packet_util.PACKET_TYPE_MAGNETOMETER,
                    packet_util.PACKET_TYPE_GYROSCOPE,
                    packet_util.PACKET_TYPE_GPS_SATELLITES,
                    packet_util.PACKET_TYPE_GPS_GROUND_SPEED
                ]:
                    if packet_type in packet_types:
                        payload_size = packet_util.PAYLOAD_SIZE[packet_type]
                        payload_format = packet_util.PAYLOAD_FORMAT[packet_type]
                        if len(self.data_buffer) - self.idx_cursor >= payload_size:
                            payload_bytes = self.data_buffer[self.idx_cursor:(self.idx_cursor + payload_size)]
                            payload = struct.unpack(payload_format, payload_bytes)
                            self.idx_cursor += payload_size

                            packet_payload_bytes += payload_bytes
                            packet_payload[packet_type] = payload
                            
                            def store_packet_data(fields: tuple[list], timestamp: float, payload: tuple) :
                                """
                                Takes a tuple of mutable field references, a timestamp, and a corresponding tuple of payload values. Assigns each value of the payload into the corresponding field. The tuples should be the same length.
                                """
                                for idx in range(len(fields)):
                                    fields[idx].append((timestamp, payload[idx]))
                                    
                            if packet_type == packet_util.PACKET_TYPE_ARM_STATUS:
                                store_packet_data((
                                        self.arm_status_1_data,
                                        self.arm_status_2_data,
                                        self.arm_status_3_data
                                    ), packet_timestamp, payload)
                            elif packet_type == packet_util.PACKET_TYPE_ALTITUDE:
                                store_packet_data((
                                        self.altitude_1_data,
                                        self.altitude_2_data,
                                    ), packet_timestamp, payload)
                            elif packet_type == packet_util.PACKET_TYPE_ACCELERATION:
                                store_packet_data((
                                        self.acceleration_x_data,
                                        self.acceleration_y_data,
                                        self.acceleration_z_data,
                                    ), packet_timestamp, payload)
                            elif packet_type == packet_util.PACKET_TYPE_GPS_COORDINATES:
                                store_packet_data((
                                        self.gps_latitude_data,
                                        self.gps_longitude_data,
                                    ), packet_timestamp, payload)
                            elif packet_type == packet_util.PACKET_TYPE_BOARD_TEMPERATURE:
                                store_packet_data((
                                    self.board_1_temperature_data,
                                    self.board_2_temperature_data,
                                    self.board_3_temperature_data,
                                    self.board_4_temperature_data
                                    ), packet_timestamp, payload)
                            elif packet_type == packet_util.PACKET_TYPE_BOARD_VOLTAGE:
                                store_packet_data((
                                    self.board_1_voltage_data,
                                    self.board_2_voltage_data,
                                    self.board_3_voltage_data,
                                    self.board_4_voltage_data
                                    ), packet_timestamp, payload)
                
                # Parse footer:
                if len(self.data_buffer) - self.idx_cursor >= 4:
                    packet_checksum_bytes = self.data_buffer[self.idx_cursor:(self.idx_cursor + 4)]
                    (packet_checksum,) = struct.unpack('>i', packet_checksum_bytes)
                    self.idx_cursor += 4
                
                # Check packet checksum:
                is_ok = False
                if self.checksum_calculator.verify_checksum(packet_types_bytes + packet_timestamp_bytes + packet_payload_bytes, packet_checksum):
                    is_ok = True
                
                # if is_ok:
                #     print(f'[OK] {packet_types_bytes.hex()} {packet_payload_bytes.hex()} {packet_checksum_bytes.hex()}')
                #     print(f'\t{packet_types} {packet_payload} {packet_checksum}')
                # else:
                #     print(f'[BAD] {packet_types_bytes.hex()} {packet_payload_bytes.hex()} {packet_checksum_bytes.hex()}')
                #     print(f'\tExpected {self.checksum_calculator.calculate_checksum(packet_types_bytes + packet_payload_bytes)}, got {packet_checksum}')

                if is_ok:
                    self.data_buffer = self.data_buffer[self.idx_cursor:]
                    self.idx_cursor = 0
                else:
                    self.data_buffer = self.data_buffer[1:]
                    self.idx_cursor = 0
                    # TODO: Need to track if we are in "network recover" state.
                
                # The basic algorithm for recovery is:
                # If crc doesn't match up, discard one byte at a time and try to parse again.
                




# Test cases
def test():
    # Test update()
    test = IliadDataController()
    config = {
        'port_name': 'COM2',
        'port_baud_rate': 9600,
        'port_stop_bits': serial.STOPBITS_ONE,
        'port_parity': serial.PARITY_NONE,
        'port_byte_size': serial.EIGHTBITS,
    }
    test.set_config(config)
    test.open()
    for i in range(1000):
        test.update()
    test.close()

    # Test packet parsing and data storage/retrieval:
    test = IliadDataController()
    test.set_config({
        'port_name': 'COM2',
        'port_baud_rate': 9600,
        'port_stop_bits': serial.STOPBITS_ONE,
        'port_parity': serial.PARITY_NONE,
        'port_byte_size': serial.EIGHTBITS,
    })
    test.open()
    port = serial.Serial(
        port='COM1',
        baudrate=9600,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
    )
    # Test arm status packet
    port.write(packet_util.create_packet(packet_util.PACKET_TYPE_ARM_STATUS, 0.0, (True, True, True)))
    for i in range(100):
        test.update()
    assert test.arm_status_1_data == [(0.0, True)]
    assert test.arm_status_2_data == [(0.0, True)]
    assert test.arm_status_3_data == [(0.0, True)]
    # Test altitude packet
    port.write(packet_util.create_packet(packet_util.PACKET_TYPE_ALTITUDE, 0.0, (1.234, 5.678)))
    for i in range(100):
        test.update()
    assert len(test.altitude_1_data) == 1
    assert len(test.altitude_2_data) == 1
    assert test.altitude_1_data[0][0] == 0.0
    assert test.altitude_2_data[0][0] == 0.0
    assert math.isclose(test.altitude_1_data[0][1], 1.234, rel_tol=1e-6) # TODO: Figure out specific tolerances.
    assert math.isclose(test.altitude_2_data[0][1], 5.678, rel_tol=1e-6)
    # Test acceleration packet
    port.write(packet_util.create_packet(packet_util.PACKET_TYPE_ACCELERATION, 0.0, (1.234, 5.678, 9.012)))
    for i in range(100):
        test.update()
    assert len(test.acceleration_x_data) == 1
    assert len(test.acceleration_y_data) == 1
    assert len(test.acceleration_z_data) == 1
    assert test.acceleration_x_data[0][0] == 0.0
    assert test.acceleration_y_data[0][0] == 0.0
    assert test.acceleration_z_data[0][0] == 0.0
    assert math.isclose(test.acceleration_x_data[0][1], 1.234, rel_tol=1e-6)
    assert math.isclose(test.acceleration_y_data[0][1], 5.678, rel_tol=1e-6)
    assert math.isclose(test.acceleration_z_data[0][1], 9.012, rel_tol=1e-6)
    # Test gps coordinates packet
    port.write(packet_util.create_packet(packet_util.PACKET_TYPE_GPS_COORDINATES, 0.0, (1.234, 5.678)))
    for i in range(100):
        test.update()
    assert len(test.gps_latitude_data) == 1
    assert len(test.gps_longitude_data) == 1
    assert test.gps_latitude_data[0][0] == 0.0
    assert test.gps_longitude_data[0][0] == 0.0
    assert math.isclose(test.gps_latitude_data[0][1], 1.234, rel_tol=1e-6)
    assert math.isclose(test.gps_longitude_data[0][1], 5.678, rel_tol=1e-6)
    # Test board temperature packet
    port.write(packet_util.create_packet(packet_util.PACKET_TYPE_BOARD_TEMPERATURE, 0.0, (1.234, 5.678, 9.012, 3.456)))
    for i in range(100):
        test.update()
    assert len(test.board_1_temperature_data) == 1
    assert len(test.board_2_temperature_data) == 1
    assert len(test.board_3_temperature_data) == 1
    assert len(test.board_4_temperature_data) == 1
    assert test.board_1_temperature_data[0][0] == 0.0
    assert test.board_2_temperature_data[0][0] == 0.0
    assert test.board_3_temperature_data[0][0] == 0.0
    assert test.board_4_temperature_data[0][0] == 0.0
    assert math.isclose(test.board_1_temperature_data[0][1], 1.234, rel_tol=1e-6)
    assert math.isclose(test.board_2_temperature_data[0][1], 5.678, rel_tol=1e-6)
    assert math.isclose(test.board_3_temperature_data[0][1], 9.012, rel_tol=1e-6)
    assert math.isclose(test.board_4_temperature_data[0][1], 3.456, rel_tol=1e-6)
