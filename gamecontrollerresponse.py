import serial
from datetime import datetime
from datetime import timedelta

ASCII_TYPE: str = 'ascii'
COMMAND_RESPONSE_LINE_ENDING: str = "\n>";


def send_command_read_response(command: str, serial_port: serial.Serial) -> str:
    ret: str = ''
    command = 'cmd:' + command + '()\n'
    serial_port.write(command.encode(ASCII_TYPE))
    serial_port.flush()
    end_time: datetime = datetime.now() + timedelta(seconds=5)
    end_found: bool = False
    while (datetime.now() < end_time) and (not end_found):
        if serial_port.in_waiting > 0:
            serial_bytes: bytes = serial_port.read(serial_port.in_waiting)
            ret_part: str = serial_bytes.decode(ASCII_TYPE)
            end_found = COMMAND_RESPONSE_LINE_ENDING in ret_part
            ret += ret_part

    if end_found:
        # remove the command echo
        ret = ret.replace(command, '')
        # remove the ending
        ret = ret.replace(COMMAND_RESPONSE_LINE_ENDING, '')

    return ret
