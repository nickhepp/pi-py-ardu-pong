from dataclasses import dataclass


@dataclass
class GameControllerData:
    player_id: int
    x_axis: int
    y_axis: int
    joystick: int
    pb1: int
    pb2: int
    pb3: int
    pb4: int

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.player_id == other.player_id and \
               self.x_axis == other.x_axis and \
               self.y_axis == other.y_axis and \
               self.joystick == other.joystick and \
               self.pb1 == other.pb1 and \
               self.pb2 == other.pb2 and \
               self.pb3 == other.pb3 and \
               self.pb4 == other.pb4
