import multiprocessing
from multiprocessing import Process, Queue
import gamecontrollerresponse
import gamecontrollerpoller

class GameController:
    def __init__(self, serial_port_name: str):
        self.serial_port_name: str = serial_port_name
        if (self.serial_port_name is not None):
            m = multiprocessing.Manager()
            self.queue: Queue = m.Queue(maxsize=10)
        else:
            self.queue = None
        self.x_axis = gamecontrollerpoller.X_AXIS_MIDDLE
        self.y_axis = gamecontrollerpoller.Y_AXIS_MIDDLE


    def has_serial_port(self) -> bool:
        return self.serial_port_name is not None


    def read_controller(self) -> bool:
        if (self.has_serial_port() and not self.queue.empty()):
            try:
                item = self.queue.get_nowait()
                self.x_axis = item[gamecontrollerpoller.X_AXIS_NAME]
                self.y_axis = item[gamecontrollerpoller.Y_AXIS_NAME]

            except:
                print("queue is empty")
