from typing import Dict, Tuple

from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ListProperty
)
from kivy.vector import Vector

import gamecontrollerpoller
import ppap
from gamecontroller import GameController
from pongball import PongBall
from screenbounds import ScreenBounds
from spawnedpongball import SpawnedPongBall


class PongPaddle(Widget):
    rgba = ListProperty([0.75, 0.5, 0.5, 1])  # will be used as background color
    score = NumericProperty(0)
    current_ball_size = NumericProperty(0)
    READY_BALL_SIZE = 10
    HORIZONTAL_ORIENTATION = 0
    VERTICAL_ORIENTATION = 1

    LOCATION_UPDATE_AMOUNT = 5

    _orientation = VERTICAL_ORIENTATION
    _game_controller = None
    player_id: int = 0
    paddle_face_direction: int = 0

    spb1: SpawnedPongBall = None
    spb2: SpawnedPongBall = None
    spb3: SpawnedPongBall = None
    spb4: SpawnedPongBall = None

    spbs: Dict[int, SpawnedPongBall] = None
    spb_directions: Dict[int, Tuple] = None


    def age_spawn_balls(self):
        if self.current_ball_size < self.READY_BALL_SIZE:
            self.current_ball_size += 1

    def get_spawned_ball(self):
        # todo: check to see if button is pressed, and if so release balls
        return None

    def set_paddle_orientation(self,
                               player_id: int,
                               orientation: int,
                               paddle_face_direction: int):
        self.player_id = player_id
        self._orientation = orientation
        self.paddle_face_direction = paddle_face_direction

        # setup the spawn balls
        self.spb1 = SpawnedPongBall()
        self.spb2 = SpawnedPongBall()
        self.spb3 = SpawnedPongBall()
        self.spb4 = SpawnedPongBall()
        self.spbs = {ppap.PB1_INDEX: self.spb1,
                     ppap.PB2_INDEX: self.spb2,
                     ppap.PB3_INDEX: self.spb3,
                     ppap.PB4_INDEX: self.spb4}

        self.spb1.set_player_info(player_id, self.rgba)
        self.parent.add_widget(self.spb1, ppap.SPAWN_BALLS_Z_INDEX)

        self.spb2.set_player_info(player_id, self.rgba)
        self.parent.add_widget(self.spb2, ppap.SPAWN_BALLS_Z_INDEX)

        self.spb3.set_player_info(player_id, self.rgba)
        self.parent.add_widget(self.spb3, ppap.SPAWN_BALLS_Z_INDEX)

        self.spb4.set_player_info(player_id, self.rgba)
        self.parent.add_widget(self.spb4, ppap.SPAWN_BALLS_Z_INDEX)

        # setup the vectors for when new spawn balls are deployed
        if paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_RIGHT:
            self.spb_directions = {
                ppap.PB1_INDEX: (ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB2_INDEX: (ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB3_INDEX: (ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB4_INDEX: (ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
            }
        elif paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_BOTTOM:
            self.spb_directions = {
                ppap.PB1_INDEX: (-ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB2_INDEX: (ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB3_INDEX: (ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB4_INDEX: (-ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
            }
        elif paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_LEFT:
            self.spb_directions = {
                ppap.PB1_INDEX: (-ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB2_INDEX: (-ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB3_INDEX: (-ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB4_INDEX: (-ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, -ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
            }
        else: #if paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_TOP:
            self.spb_directions = {
                ppap.PB1_INDEX: (-ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB2_INDEX: (ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED),
                ppap.PB3_INDEX: (ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
                ppap.PB4_INDEX: (-ppap.SPAWN_BALL_INITIAL_MAJOR_COMPONENT_SPEED, ppap.SPAWN_BALL_INITIAL_MINOR_COMPONENT_SPEED),
            }


    def set_game_controller(self, game_controller: GameController):
        self._game_controller = game_controller

    def update_location(self, screen_bounds: ScreenBounds):
        # move the paddle
        if self._orientation == self.VERTICAL_ORIENTATION:
            if self._game_controller.y_axis == gamecontrollerpoller.Y_AXIS_UP:
                self.center_y += self.LOCATION_UPDATE_AMOUNT
            elif self._game_controller.y_axis == gamecontrollerpoller.Y_AXIS_DOWN:
                self.center_y -= self.LOCATION_UPDATE_AMOUNT

            if self.top > screen_bounds.top:
                self.top = screen_bounds.top
            elif self.y < screen_bounds.bottom:
                self.y = screen_bounds.bottom

        if self._orientation == self.HORIZONTAL_ORIENTATION:
            if self._game_controller.x_axis == gamecontrollerpoller.X_AXIS_LEFT:
                self.center_x -= self.LOCATION_UPDATE_AMOUNT
            elif self._game_controller.x_axis == gamecontrollerpoller.X_AXIS_RIGHT:
                self.center_x += self.LOCATION_UPDATE_AMOUNT

            if self.right > screen_bounds.right:
                self.right = screen_bounds.right
            elif self.x < screen_bounds.left:
                self.x = screen_bounds.left

        # now figure out where the spawn balls go
        ball_size = self.spb1.width
        pball_center_x: int
        pball_center_y: int
        if self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_RIGHT:
            pball_center_y = self.center_y
            pball_center_x = self.right + ball_size
        elif self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_LEFT:
            pball_center_y = self.center_y
            pball_center_x = self.x - ball_size
        elif self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_TOP:
            pball_center_x = self.center_x
            pball_center_y = self.top + ball_size
        else: # self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_BOTTOM:
            pball_center_x = self.center_x
            pball_center_y = self.y - ball_size

        self.spb1.center_x = pball_center_x - (0.5 * ball_size)
        self.spb1.center_y = pball_center_y + (0.5 * ball_size)

        self.spb2.center_x = pball_center_x + (0.5 * ball_size)
        self.spb2.center_y = pball_center_y + (0.5 * ball_size)

        self.spb3.center_x = pball_center_x + (0.5 * ball_size)
        self.spb3.center_y = pball_center_y - (0.5 * ball_size)

        self.spb4.center_x = pball_center_x - (0.5 * ball_size)
        self.spb4.center_y = pball_center_y - (0.5 * ball_size)

        for pb_index in self.spbs:
            self.spbs[pb_index].age_ball()

    def get_spawned_balls(self) -> []:
        spawn_balls: [] = []
        for pb_index in self.spbs:
            button_pressed = self._game_controller.get_push_button(pb_index)
            if (button_pressed == ppap.PUSH_BUTTON_PRESSED) and self.spbs[pb_index].get_is_ready():
                pb = PongBall()
                pb.set_bounced_paddle(self)
                pb.velocity_x = self.spb_directions[pb_index][0]
                pb.velocity_y = self.spb_directions[pb_index][1]
                pb.center = self.spbs[pb_index].center
                pb.rgba = self.rgba
                spawn_balls.append(pb)
                self.spbs[pb_index].reset_ball_age()

        return spawn_balls
        #if self._game_controller.pb1 == ppap.PUSH_BUTTON_PRESSED and self.spb1.get_is_ready():



    def score_against(self, ball):
        # this paddle is scored against, take away the score
        self.score -= 1
        # add one to the scoring one
        b_paddle = ball.get_bounced_paddle()
        if b_paddle is not None:
            b_paddle.score += 1

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            ball.set_bounced_paddle(self)
            ball.rgba = self.rgba
            # grab the initial ball velocity
            vx, vy = ball.velocity
            # find how high up the paddle it was hit
            if self._orientation == self.HORIZONTAL_ORIENTATION:
                offset_x = (ball.center_x - self.center_x) / (self.width / 2)
                bounced = Vector(vx, -1 * vy)
                vel = bounced * 1.1
                ball.velocity = vel.x + offset_x, vel.y
                if self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_BOTTOM:
                    ball.y = self.y - 1 - ball.height
                    if ball.velocity_y > 0:
                        ball.velocity_y = -ball.velocity_y
                else: #self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_TOP:
                    ball.y = self.top + 1
                    if ball.velocity_y < 0:
                        ball.velocity_y = -ball.velocity_y

            else: # self._orientation == self.VERTICAL_ORIENTATION
                offset_y = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                vel = bounced * 1.1
                ball.velocity = vel.x, vel.y + offset_y
                if self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_RIGHT:
                    ball.x = self.right + 1
                    if ball.velocity_x < 0:
                        ball.velocity_x = -ball.velocity_x
                else: #self.paddle_face_direction == ppap.PADDLE_FACE_DIRECTION_LEFT
                    ball.right = self.x - 1
                    if ball.velocity_x > 0:
                        ball.velocity_x = -ball.velocity_x

