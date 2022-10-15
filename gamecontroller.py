import multiprocessing
from multiprocessing import Process, Queue
import gamecontrollerresponse
import gamecontrollerpoller
from gamecontrollerdata import GameControllerData


class GameController:
    def __init__(self, player_id: int, serial_port_name: str):

        self.player_id: int = player_id
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
                item: GameControllerData = self.queue.get_nowait()
                self.x_axis = item.x_axis
                self.y_axis = item.y_axis

            except:
                print("queue is empty")
