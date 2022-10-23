from dataclasses import dataclass
from multiprocessing import Queue


@dataclass
class PossibleSerialPort:
    serial_port_name: str
    player_id: int
    queue: Queue
