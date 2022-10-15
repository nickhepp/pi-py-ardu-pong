from time import sleep

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
from possibleserialport import PossibleSerialPort
from regiondetector import RegionDetector
from kivy.uix.label import Label
from screenbounds import ScreenBounds
from location import Location
from pongball import PongBall
from kivy.core.window import Window
import ppap

# consider using async IO to complete coordination between threads
# https://github.com/pyserial/pyserial-asyncio
# https://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html

# consider using multiprocess communications -- where here is the process breakdown:
# 1) original process runs the kivy app
# 2) second process runs the serial IO
# The hope of the multi process architecture is that the IO operations
# wont block the app from running as expected.


# TODO: single process with single queue

# TODO: make paddles bounce out for extra speed boost of ball, and then temporarily pause or become translucent
#       not able to bounce the balls for a duration (1 sec?)

# TODO: multi balls

# TODO: pressing a button can launch a ball

PLAYER1_CONTROLLER_COLOR: int = 0xFF0000
PLAYER2_CONTROLLER_COLOR: int = 0x0000FF
PLAYER3_CONTROLLER_COLOR: int = 0x00FF00
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
        gcs.append(gc)


class PongGame(Widget):
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
    game_controllers = ListProperty([])
    controllers = ListProperty([])

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
        self.game_controller1 = GameController(
            ppap.PLAYER1_ID,
            get_serial_by_color(PLAYER1_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player1.set_game_controller(self.game_controller1)
        self.player1.set_paddle_orientation(ppap.PLAYER1_ID,
                                            self.VERTICAL_ORIENTATION,
                                            ppap.PADDLE_FACE_DIRECTION_RIGHT)
        self.region1.set_paddle(self.player1)

        # green
        self.game_controller2 = GameController(
            ppap.PLAYER2_ID,
            get_serial_by_color(PLAYER2_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player2.set_game_controller(self.game_controller2)
        self.player2.set_paddle_orientation(ppap.PLAYER2_ID,
                                            self.HORIZONTAL_ORIENTATION,
                                            ppap.PADDLE_FACE_DIRECTION_BOTTOM)
        self.region2.set_paddle(self.player2)

        # blue
        self.game_controller3 = GameController(
            ppap.PLAYER3_ID,
            get_serial_by_color(PLAYER3_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player3.set_game_controller(self.game_controller3)
        self.player3.set_paddle_orientation(ppap.PLAYER3_ID,
                                            self.VERTICAL_ORIENTATION,
                                            ppap.PADDLE_FACE_DIRECTION_LEFT)
        self.region3.set_paddle(self.player3)

        # yellow
        self.game_controller4 = GameController(
            ppap.PLAYER4_ID,
            get_serial_by_color(PLAYER4_CONTROLLER_COLOR, serial_ports_by_colors))
        self.player4.set_game_controller(self.game_controller4)
        self.player4.set_paddle_orientation(ppap.PLAYER4_ID,
                                            self.HORIZONTAL_ORIENTATION,
                                            ppap.PADDLE_FACE_DIRECTION_TOP)
        self.region4.set_paddle(self.player4)

        self.game_controllers = []
        attempt_add_game_controller(self.game_controllers, self.game_controller1)
        attempt_add_game_controller(self.game_controllers, self.game_controller2)
        attempt_add_game_controller(self.game_controllers, self.game_controller3)
        attempt_add_game_controller(self.game_controllers, self.game_controller4)

        self.controllers.append(self.game_controller1)
        self.controllers.append(self.game_controller2)
        self.controllers.append(self.game_controller3)
        self.controllers.append(self.game_controller4)

        self.player_ids_to_players = {ppap.PLAYER1_ID: self.player1,
                                      ppap.PLAYER2_ID: self.player2,
                                      ppap.PLAYER3_ID: self.player3,
                                      ppap.PLAYER4_ID: self.player4, }
        ##def class_init(self):

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

        # see if we need to create balls
        self.check_create_ball()

        # make the balls move
        for ball in self.balls:
            ball.move()

        # read the controller IO
        for controller in self.controllers:
            controller.read_controller()

        screen_bounds = ScreenBounds(self.x, self.y, self.top, self.right)

        # update the paddle locations
        for player_id in self.player_ids_to_players:
            self.player_ids_to_players[player_id].update_location(screen_bounds)
            spawned_balls: [] = self.player_ids_to_players[player_id].get_spawned_balls()
            for spawned_ball in spawned_balls:
                self.balls.append(spawned_ball)
                self.add_widget(spawned_ball)

        # make the balls bounce off the paddles
        scored_player_id: int
        for ball in self.balls:

            # see if the ball is going to bounce
            for player_id in self.player_ids_to_players:
                self.player_ids_to_players[player_id].bounce_ball(ball)

            ball_location = Location(ball.x, ball.y)
            ball_region = self.region_detector.get_region(screen_bounds, ball_location)
            scored_player_id = self.region_detector.get_scored_on_player_from_ball_location(
                ball_region,
                screen_bounds,
                ball_location)

            if scored_player_id in self.player_ids_to_players:
                self.player_ids_to_players[scored_player_id].score_against(ball)
                self.remove_widget(ball)
                self.balls.remove(ball)
                self.check_create_ball()

        if self.show_debug_labels:
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


    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player3.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.class_init()
        Clock.schedule_interval(game.update, 1.0 / ppap.UPDATES_PER_SECOND)

        if len(game.game_controllers) > 0:
            #p = Process(target=run_controller, args=(game.game_controllers,))
            gcs: [] = []
            for gc in game.game_controllers:
                #gcs.append([])
                #sp = {'player_id': gc.player_id, 'serial_port_name': gc.serial_port_name, 'queue': gc.queue}
                sp = PossibleSerialPort(serial_port_name=gc.serial_port_name,
                     player_id=gc.player_id,
                     queue=gc.queue)
                gcs.append(sp)

            p = Process(target=run_controller, args=(gcs,))
            p.start()

        return game


def run_controller(gcs: []):
    gcp = GameControllerPoller(gcs)
    while True:
        gcp.read_physical_controller()


if __name__ == '__main__':
    #Window.fullscreen = True
    PongApp().run()
