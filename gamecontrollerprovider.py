import serial
import serial.tools.list_ports as port_list
import gamecontrollerresponse
from datetime import datetime
from datetime import timedelta
import time


class GameControllerProvider:
    def __init__(self):
        # nothing for now
        self.RED_START = 'red='
        self.GREEN_START = 'green='
        self.BLUE_START = 'blue='

    def get_controllers(self) -> {}:
        ports_to_colors: {} = {}
        try:
            potential_ports = list(port_list.comports())
            ports = []
            for p in potential_ports:
                # filter out things we dont want
                if not 'Intel(R) Active Management Technology' in p.description:
                    ports.append(p)

            for p in ports:
                serial_port = serial.Serial(
                    port=p.device, baudrate=115200, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE
                )

                # just flush the stuff
                gamecontrollerresponse.send_command_read_response('', serial_port)
                gamecontrollerresponse.send_command_read_response('', serial_port)

                gc_clrs: str = gamecontrollerresponse.send_command_read_response('get_colors', serial_port)

                red_location: int = gc_clrs.find(self.RED_START)
                red_comma: int = gc_clrs.find(',', red_location)
                green_location: int = gc_clrs.find(self.GREEN_START)
                green_comma: int = gc_clrs.find(',', green_location)
                blue_location: int = gc_clrs.find(self.BLUE_START)
                if ((red_location != -1) and
                        (red_comma != -1) and
                        (green_location != -1) and
                        (green_comma != -1) and
                        (blue_location != -1)):
                    # push the location to the start of the number
                    red_num = red_location + len(self.RED_START)
                    green_num = green_location + len(self.GREEN_START)
                    blue_num = blue_location + len(self.BLUE_START)

                    red_num_str: str = gc_clrs[red_num:red_comma] #.strip(" ,")
                    green_num_str: str = gc_clrs[green_num:green_comma] #.strip(" ,")
                    blue_num_str: str = gc_clrs[blue_num:]

                    if (red_num_str.isnumeric() and green_num_str.isnumeric() and blue_num_str.isnumeric()):
                        red_val = int(red_num_str)
                        green_val = int(green_num_str)
                        blue_val = int(blue_num_str)
                        color_val = (red_val << 16) | (green_val << 8) | (blue_val << 0)
                        color_val_str = hex(color_val)
                        ports_to_colors[color_val_str] = serial_port

        except Exception as exc:
            print('Issue starting controllers')
            print(exc.args)

        return ports_to_colors
