import pongball, pongpaddle, scoreregion
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    ObjectProperty, ListProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import random
import gamecontroller
import gamecontrollerprovider
from multiprocessing import Process, Queue, Pool

# consider using async IO to complete coordination between threads
# https://github.com/pyserial/pyserial-asyncio
# https://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html

# consider using multiprocess communications -- where here is the process breakdown:
# 1) original process runs the kivy app
# 2) second process runs the serial IO
# The hope of the multi process architecture is that the IO operations
# wont block the app from runnnig as expected.

PLAYER1_CONTROLLER_COLOR: int = 0xFF0000
PLAYER2_CONTROLLER_COLOR: int = 0x00FF00
PLAYER3_CONTROLLER_COLOR: int = 0x0000FF
PLAYER4_CONTROLLER_COLOR: int = 0xFFFF00


def get_serial_by_color(clr: int, serial_ports_by_colors: {}):
    clr_str = hex(clr)
    serial_port = None
    if clr_str in serial_ports_by_colors:
        serial_port = serial_ports_by_colors[clr_str]
    return serial_port


class PongGame(Widget):
    ball = ObjectProperty(None)

    player1 = ObjectProperty(None)
    region1 = ObjectProperty(None)

    player2 = ObjectProperty(None)
    region2 = ObjectProperty(None)

    player3 = ObjectProperty(None)
    region3 = ObjectProperty(None)

    player4 = ObjectProperty(None)
    region4 = ObjectProperty(None)

    balls = ListProperty([])
    players = ListProperty([])

    HORIZONTAL_ORIENTATION = 0
    VERTICAL_ORIENTATION = 1

    def class_init(self):
        gc_provider = gamecontrollerprovider.GameControllerProvider()

        serial_ports_by_colors = gc_provider.get_controllers()

        # red, color, com_port, queue
        self.player1.set_paddle_orientation(self.VERTICAL_ORIENTATION)
        self.region1.set_paddle(self.player1)
        self.game_controller1 = gamecontroller.GameController(
            get_serial_by_color(PLAYER1_CONTROLLER_COLOR, serial_ports_by_colors))

        # green
        self.player2.set_paddle_orientation(self.VERTICAL_ORIENTATION)
        self.region2.set_paddle(self.player2)
        self.game_controller2 = gamecontroller.GameController(
            get_serial_by_color(PLAYER2_CONTROLLER_COLOR, serial_ports_by_colors))

        # blue
        self.player3.set_paddle_orientation(self.HORIZONTAL_ORIENTATION)
        self.region3.set_paddle(self.player3)
        self.game_controller3 = gamecontroller.GameController(
            get_serial_by_color(PLAYER3_CONTROLLER_COLOR, serial_ports_by_colors))

        # yellow
        self.player4.set_paddle_orientation(self.HORIZONTAL_ORIENTATION)
        self.region4.set_paddle(self.player4)
        self.game_controller4 = gamecontroller.GameController(
            get_serial_by_color(PLAYER4_CONTROLLER_COLOR, serial_ports_by_colors))

        self.game_controllers = []
        if (self.game_controller1.has_controller()):
            self.game_controllers.append(self.game_controller1)
        if (self.game_controller2.has_controller()):
            self.game_controllers.append(self.game_controller2)
        if (self.game_controller3.has_controller()):
            self.game_controllers.append(self.game_controller3)
        if (self.game_controller4.has_controller()):
            self.game_controllers.append(self.game_controller4)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        self.player3.bounce_ball(self.ball)
        self.player4.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        has_scored = False

        if not has_scored and self.region1.check_for_score(self.ball):
            has_scored = True
        elif not has_scored and self.region2.check_for_score(self.ball):
            has_scored = True
        elif not has_scored and self.region3.check_for_score(self.ball):
            has_scored = True
        elif not has_scored and self.region4.check_for_score(self.ball):
            has_scored = True

        if has_scored:
            rand_val: int = random.randint(0, 3)
            if rand_val == 0:
                self.serve_ball(vel=(4, 0))
            elif rand_val == 1:
                self.serve_ball(vel=(-4, 0))
            elif rand_val == 2:
                self.serve_ball(vel=(0, 4))
            else:  # 3
                self.serve_ball(vel=(0, -4))

        # if self.ball.x < self.x:
        #    self.player2.score += 1

        # if self.ball.right > self.width:
        #    self.player1.score += 1
        #    self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.class_init()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)

        # with Pool(processes=len(game.game_controllers)) as pool:
        #    pool.map(run_controller, game.game_controllers)

        return game


def run_controller(gc: gamecontroller.GameController):
    is_connected: bool = gc.connected
    if not is_connected:
        is_connected = gc.try_connect()


if __name__ == '__main__':
    PongApp().run()
