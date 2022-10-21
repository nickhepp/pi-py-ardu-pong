from datetime import datetime
from datetime import timedelta
from multiprocessing import Queue

from serial import Serial

import gamecontrollerresponse
import ppap
import serialportfactory
from time import sleep
from typing import Type, Dict
from possibleserialport import PossibleSerialPort
from gamecontrollerdata import GameControllerData

SENSOR_DATA_START = 'kit:'
LEFT_RIGHT_INDEX = 0
UP_DOWN_INDEX = 1
JOY_BUTTON_INDEX = 2
PB1_INDEX = 3
PB2_INDEX = 4
PB3_INDEX = 5
PB4_INDEX = 6

LEFT_RANGE = UP_RANGE = dict(min=ppap.AXIS_MIDPOINT + ppap.AXIS_DELTA, max=1024)
RIGHT_RANGE = DOWN_RANGE = dict(min=0, max=ppap.AXIS_MIDPOINT - ppap.AXIS_DELTA)

X_AXIS_NAME = 'x_axis'
X_AXIS_LEFT = -1
X_AXIS_MIDDLE = 0
X_AXIS_RIGHT = 1

Y_AXIS_NAME = 'y_axis'
Y_AXIS_UP = 1
Y_AXIS_MIDDLE = 0
Y_AXIS_DOWN = -1


class GameControllerPoller:
    def __init__(self, serial_ports: Type[PossibleSerialPort]):
        self.serial_ports: Dict[int, Serial] = {}
        self.queues: Dict[int, Queue] = {}
        self.previous_data: Dict[int, GameControllerData] = {}
        self.next_time = None

        for serial_port in serial_ports:
            sp = serialportfactory.get_serial_port(serial_port.serial_port_name)
            self.serial_ports[serial_port.player_id] = sp
            self.queues[serial_port.player_id] = serial_port.queue

    def put_sensor_data(self, player_id: int):
        if self.queues[player_id].full():
            return

        sensor_data: str = gamecontrollerresponse.send_command_read_response(
            'edpf_kit_read',
            self.serial_ports[player_id])

        # look to see if this is the data we are looking for
        if sensor_data.startswith(SENSOR_DATA_START):
            # strip the beginning
            sensor_data = sensor_data[len(SENSOR_DATA_START):]
            # strip any leftover cruft
            sensor_data = sensor_data.strip('\r\n')

            sensor_data_vals = [int(item) for item in sensor_data.split(',') if item.isdigit()]
            x_axis_val: int = sensor_data_vals[LEFT_RIGHT_INDEX]
            y_axis_val: int = sensor_data_vals[UP_DOWN_INDEX]
            joystick_val: int = sensor_data_vals[JOY_BUTTON_INDEX]
            pb1_val: int = sensor_data_vals[PB1_INDEX]
            pb2_val: int = sensor_data_vals[PB2_INDEX]
            pb3_val: int = sensor_data_vals[PB3_INDEX]
            pb4_val: int = sensor_data_vals[PB4_INDEX]

            if LEFT_RANGE['min'] <= x_axis_val <= LEFT_RANGE['max']:
                x_axis_val = X_AXIS_LEFT
            elif RIGHT_RANGE['min'] <= x_axis_val <= RIGHT_RANGE['max']:
                x_axis_val = X_AXIS_RIGHT
            else:
                x_axis_val = X_AXIS_MIDDLE

            if UP_RANGE['min'] <= y_axis_val <= UP_RANGE['max']:
                y_axis_val = Y_AXIS_UP
            elif DOWN_RANGE['min'] <= y_axis_val <= DOWN_RANGE['max']:
                y_axis_val = Y_AXIS_DOWN
            else:
                y_axis_val = Y_AXIS_MIDDLE

            try:
                gcd: GameControllerData = GameControllerData(player_id=player_id,
                                                             x_axis=x_axis_val,
                                                             y_axis=y_axis_val,
                                                             joystick=joystick_val,
                                                             pb1=pb1_val,
                                                             pb2=pb2_val,
                                                             pb3=pb3_val,
                                                             pb4=pb4_val)

                self.queues[player_id].put_nowait(gcd)
                #if (player_id not in self.previous_data) or \
                #        self.previous_data[player_id] != gcd:
                #    self.queues[player_id].put_nowait(gcd)
                #    self.previous_data[player_id] = gcd
            except Exception as exc:
                exc = exc

    def read_physical_controller(self):
        start_time: datetime = datetime.now()
        if (self.next_time is None) or (start_time > self.next_time):
            #self.next_time = start_time + timedelta(seconds=0.333)

            # read all the controllers
            for player_id in self.serial_ports:
                self.put_sensor_data(player_id)

        else:
            sleep(.050)
