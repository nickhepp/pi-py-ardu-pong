from multiprocessing import Process, Queue


class GameController:
    def __init__(self, serial_port):
        self.serial_port = serial_port
        if (self.serial_port is not None):
            self.queue = Queue()
        else:
            self.queue = None

    def has_controller(self) -> bool:
        return self.serial_port is not None

