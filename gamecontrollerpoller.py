from multiprocessing import Process, Queue
import gamecontrollerresponse
import serialportfactory
from time import sleep

SENSOR_DATA_START = 'kit:'
LEFT_RIGHT_INDEX = 0
UP_DOWN_INDEX = 1
JOY_BUTTON_INDEX = 2
PB1_INDEX = 3
PB2_INDEX = 4
PB3_INDEX = 5
PB4_INDEX = 6

LEFT_RANGE = UP_RANGE = dict(min=700, max=1024)
RIGHT_RANGE = DOWN_RANGE = dict(min=0, max=300)

X_AXIS_NAME = 'x_axis'
X_AXIS_LEFT = -1
X_AXIS_MIDDLE = 0
X_AXIS_RIGHT = 1

Y_AXIS_NAME = 'y_axis'
Y_AXIS_UP = 1
Y_AXIS_MIDDLE = 0
Y_AXIS_DOWN = -1

class GameControllerPoller:
    def __init__(self, serial_port_name: str, queue: Queue):
        self.serial_port_name: str = serial_port_name
        self.queue = queue
        self.serial_port = serialportfactory.get_serial_port(serial_port_name)

    def read_physical_controller(self):
        if self.queue.full():
            return

        sleep(0.333)
        sensor_data: str = gamecontrollerresponse.send_command_read_response('edpf_kit_read', self.serial_port)


        # look to see if this is the data we are looking for
        if sensor_data.startswith(SENSOR_DATA_START):
            # strip the beginning
            sensor_data = sensor_data[len(SENSOR_DATA_START):]
            # strip any left over cruft
            sensor_data = sensor_data.strip('\r\n')

            sensor_data_vals = [int(item) for item in sensor_data.split(',') if item.isdigit()]
            x_axis_val: int = sensor_data_vals[LEFT_RIGHT_INDEX]
            y_axis_val: int = sensor_data_vals[UP_DOWN_INDEX]
            joystick_val: int = sensor_data_vals[JOY_BUTTON_INDEX]
            pb1_val: int = sensor_data_vals[PB1_INDEX]
            pb2_val: int = sensor_data_vals[PB2_INDEX]
            pb3_val: int = sensor_data_vals[PB3_INDEX]
            pb4_val: int = sensor_data_vals[PB4_INDEX]

            gc_vals = {}
            if LEFT_RANGE['min'] <= x_axis_val <= LEFT_RANGE['max']:
                gc_vals[X_AXIS_NAME] = X_AXIS_LEFT
            elif RIGHT_RANGE['min'] <= x_axis_val <= RIGHT_RANGE['max']:
                gc_vals[X_AXIS_NAME] = X_AXIS_RIGHT
            else:
                gc_vals[X_AXIS_NAME] = X_AXIS_MIDDLE

            if UP_RANGE['min'] <= y_axis_val <= UP_RANGE['max']:
                gc_vals[Y_AXIS_NAME] = Y_AXIS_UP
            elif DOWN_RANGE['min'] <= y_axis_val <= DOWN_RANGE['max']:
                gc_vals[Y_AXIS_NAME] = Y_AXIS_DOWN
            else:
                gc_vals[Y_AXIS_NAME] = Y_AXIS_MIDDLE

            try:
                self.queue.put_nowait(gc_vals)
            except Exception as exc:
                exc = exc
                # stuff