import multiprocessing
from multiprocessing import Queue
import gamecontrollerpoller
import ppap
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
        self.pb1: int = ppap.PUSH_BUTTON_NOT_PRESSED
        self.pb2: int = ppap.PUSH_BUTTON_NOT_PRESSED
        self.pb3: int = ppap.PUSH_BUTTON_NOT_PRESSED
        self.pb4: int = ppap.PUSH_BUTTON_NOT_PRESSED
        self.joystick: int = ppap.PUSH_BUTTON_NOT_PRESSED

    def has_serial_port(self) -> bool:
        return self.serial_port_name is not None

    def get_push_button(self, button_index: int) -> int:
        pressed: int = ppap.PUSH_BUTTON_NOT_PRESSED
        if self.joystick == ppap.PUSH_BUTTON_PRESSED:
            pressed = ppap.PUSH_BUTTON_PRESSED
        elif button_index == ppap.PB1_INDEX:
            pressed = self.pb1
        elif button_index == ppap.PB2_INDEX:
            pressed = self.pb2
        elif button_index == ppap.PB3_INDEX:
            pressed = self.pb3
        else: #  button_index == ppap.PB4_INDEX
            pressed = self.pb4
        return pressed

    def read_controller(self) -> bool:
        if (self.has_serial_port() and not self.queue.empty()):
            try:
                item: GameControllerData = self.queue.get_nowait()
                self.x_axis = item.x_axis
                self.y_axis = item.y_axis
                self.pb1 = item.pb1
                self.pb2 = item.pb2
                self.pb3 = item.pb3
                self.pb4 = item.pb4
                self.joystick = item.joystick
            except:
                print("queue is empty")
