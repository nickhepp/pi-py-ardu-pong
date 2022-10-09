import pongball, pongpaddle, scoreregion
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    ObjectProperty, ListProperty
)
from kivy.clock import Clock
import random
from gamecontroller import GameController
import gamecontrollerprovider
from multiprocessing import Process, Queue, Pool
from gamecontrollerpoller import GameControllerPoller
from regiondetector import RegionDetector
from kivy.uix.label import Label
from screenbounds import ScreenBounds
from location import Location
from pongball import PongBall
import ppap

# consider using async IO to complete coordination between threads
# https://github.com/pyserial/pyserial-asyncio
# https://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html

# consider using multiprocess communications -- where here is the process breakdown:
# 1) original process runs the kivy app
# 2) second process runs the serial IO
# The hope of the multi process architecture is that the IO operations
# wont block the app from running as expected.

# TODO: fix ball scoring mechanics

# TODO: when paddle hits a ball transport ball past the paddle so it doesnt go past it like it does sometimes

# TODO: scoring on a side subtracts a point from that side

# TODO: single process with single queue

# TODO: dont let paddles go off screen

# TODO: make paddles bounce out for extra speed boost of ball, and then temporarily pause or become translucent
#       not able to bounce the balls for a duration (1 sec?)

# TODO: multi balls

# TODO: pressing a button can launch a ball

PLAYER1_CONTROLLER_COLOR: int = 0xFF0000
PLAYER2_CONTROLLER_COLOR: int = 0x00FF00
PLAYER3_CONTROLLER_COLOR: int = 0x0000FF
PLAYER4_CONTROLLER_COLOR: int = 0xFFFF00

SERIAL_PORT_NAME_NAME = 'serial_port_name'
QUEUE_NAME = 'queue'


def get_serial_by_color(clr: int, serial_ports_by_colors: {}):
    clr_str = hex(clr)
    serial_port = None
    if clr_str in serial_ports_by_colors:
        serial_port = serial_ports_by_colors[clr_str]
    return serial_port


def attempt_add_game_controller(gcs: [], gc: GameController):
    if gc.has_serial_port():
        gcs.append({
            SERIAL_PORT_NAME_NAME: gc.serial_port_name,
            QUEUE_NAME: gc.queue})


class PongGame(Widget):
    ball = ObjectProperty(None)
    balls = []

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

    player_ids_to_players = {}

    region_detector = RegionDetector()

    show_debug_labels = True

    if show_debug_labels:
        btm_left_lbl = Label()
        btm_left_lbl.text = 'btm_left'

        btm_right_lbl = Label()
        btm_right_lbl.text = 'btm_right'

        top_left_lbl = Label()
        top_left_lbl.text = 'top_left'

        top_right_lbl = Label()
        top_right_lbl.text = 'top_right'

        region_lbl = Label()
        region_lbl.text = 'region'

    def class_init(self):
        if self.show_debug_labels:
            self.add_widget(self.btm_left_lbl)
            self.add_widget(self.btm_right_lbl)
            self.add_widget(self.top_left_lbl)
            self.add_widget(self.top_right_lbl)
            self.add_widget(self.region_lbl)

        gc_provider = gamecontrollerprovider.GameControllerProvider()

        serial_ports_by_colors = gc_provider.get_controllers()

        # red, color, com_port, queue
        self.game_controller1 = GameController(get_serial_by_color(PLAYER1_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player1.set_game_controller(self.game_controller1)
        self.player1.set_paddle_orientation(ppap.PLAYER1_ID, self.VERTICAL_ORIENTATION)
        self.region1.set_paddle(self.player1)

        # green
        self.game_controller2 = GameController(
            get_serial_by_color(PLAYER2_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player2.set_game_controller(self.game_controller2)
        self.player2.set_paddle_orientation(ppap.PLAYER2_ID, self.VERTICAL_ORIENTATION)
        self.region2.set_paddle(self.player2)

        # blue
        self.game_controller3 = GameController(
            get_serial_by_color(PLAYER3_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player3.set_game_controller(self.game_controller3)
        self.player3.set_paddle_orientation(ppap.PLAYER3_ID, self.HORIZONTAL_ORIENTATION)
        self.region3.set_paddle(self.player3)

        # yellow
        self.game_controller4 = GameController(
            get_serial_by_color(PLAYER4_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player4.set_game_controller(self.game_controller4)
        self.player4.set_paddle_orientation(ppap.PLAYER4_ID, self.HORIZONTAL_ORIENTATION)
        self.region4.set_paddle(self.player4)

        self.game_controllers = []
        attempt_add_game_controller(self.game_controllers, self.game_controller1)
        attempt_add_game_controller(self.game_controllers, self.game_controller2)
        attempt_add_game_controller(self.game_controllers, self.game_controller3)
        attempt_add_game_controller(self.game_controllers, self.game_controller4)

        self.player_ids_to_players = {ppap.PLAYER1_ID: self.player1,
                                      ppap.PLAYER2_ID: self.player2,
                                      ppap.PLAYER3_ID: self.player3,
                                      ppap.PLAYER4_ID: self.player4, }

    def serve_ball(self, vel=(4, 0)):
        # remove the existing one
        #if self.ball is not None and self.ball.initialized:
        #    self.remove_widget(self.ball)
        #elif self.ball is not None:
        #    self.ball.initialized = True
        #else:
        #    # add the next one
        #    self.ball = PongBall()
        #    self.add_widget(self.ball)
        self.ball.center = self.center
        self.ball.velocity = vel

    def check_create_ball(self):
        if len(self.balls) == 0:
            next_ball = PongBall()
            self.balls.append(next_ball)
            self.add_widget(next_ball)

            rand_x_vel = 4 * (random.random() - 0.5)
            rand_y_vel = 4 * (random.random() - 0.5)
            next_ball.center = self.center
            next_ball.velocity = (rand_x_vel, rand_y_vel)


    def update(self, dt):

        self.check_create_ball()
        for ball in self.balls:
            ball.move()


        self.ball.move()

        self.game_controller1.read_controller()
        self.player1.update_location()
        self.game_controller2.read_controller()
        self.player2.update_location()
        self.game_controller3.read_controller()
        self.player3.update_location()
        self.game_controller4.read_controller()
        self.player4.update_location()

        # make the balls bounce off the paddles

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        self.player3.bounce_ball(self.ball)
        self.player4.bounce_ball(self.ball)

        # now check for scoring
        screen_bounds = ScreenBounds(self.x, self.y, self.top, self.right)
        ball_location = Location(self.ball.x, self.ball.y)
        ball_region = self.region_detector.get_region(screen_bounds, ball_location)
        scored_player_id = self.region_detector.get_scored_on_player_from_ball_location(
            ball_region,
            screen_bounds,
            ball_location)

        # went of to a side to score point?
        has_scored = False

        if scored_player_id in self.player_ids_to_players:
            self.player_ids_to_players[scored_player_id].score_against(self.ball)
            has_scored = True

        # if not has_scored and self.region1.check_for_score(self.ball):
        #    has_scored = True
        # elif not has_scored and self.region2.check_for_score(self.ball):
        #    has_scored = True
        # elif not has_scored and self.region3.check_for_score(self.ball):
        #    has_scored = True
        # elif not has_scored and self.region4.check_for_score(self.ball):
        #    has_scored = True

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

        if (self.show_debug_labels):
            self.btm_left_lbl.x = self.x + 10
            self.btm_left_lbl.y = self.y + 10

            self.btm_right_lbl.x = self.right - 10 - self.btm_left_lbl.width
            self.btm_right_lbl.y = self.y + 10

            self.top_left_lbl.x = self.x + 10
            self.top_left_lbl.y = self.top - 10 - self.top_left_lbl.height

            self.top_right_lbl.x = self.right - 10 - self.btm_left_lbl.width
            self.top_right_lbl.y = self.top - 10 - self.top_left_lbl.height

            self.region_lbl.center_x = self.center_x
            self.region_lbl.center_y = self.center_y
            self.region_lbl.text = ppap.get_player_id_desc(scored_player_id)

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

        if len(game.game_controllers) > 0:
            for gc in game.game_controllers:
                p = Process(target=run_controller, args=(gc,))
                p.start()

        return game


def run_controller(port_args: {}):
    gcp = GameControllerPoller(port_args[SERIAL_PORT_NAME_NAME], port_args[QUEUE_NAME])

    while True:
        gcp.read_physical_controller()
        # print(port_args[SERIAL_PORT_NAME_NAME])
        # time.sleep(0.500)


if __name__ == '__main__':
    PongApp().run()
