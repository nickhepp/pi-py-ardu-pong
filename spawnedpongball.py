from pongball import PongBall
import ppap


class SpawnedPongBall(PongBall):
    _ball_age = 0
    _not_ready_color = None
    _ready_color = None
    _player_id: int = None
    _ready: bool = False

    def get_is_ready(self):
        return self._ready

    def age_ball(self):
        self._ball_age += 1
        if self._ball_age < ppap.AGE_BALL_UPDATES:
            self.rgba = self._not_ready_color
            self._ready = False
        else:
            self.rgba = self._ready_color
            self._ready = True

    def set_player_info(self, player_id: int, color):
        self._player_id = player_id
        self._ready_color = color
        self._not_ready_color = [color[0], color[1], color[2], 0.5]


