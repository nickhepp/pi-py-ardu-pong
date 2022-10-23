import serial


def get_serial_port(name: str) -> serial.Serial:
    serial_port = serial.Serial(
        port=name, baudrate=115200, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE
    )
    return serial_port

