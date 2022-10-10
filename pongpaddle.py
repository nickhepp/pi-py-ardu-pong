from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ListProperty
)
from kivy.vector import Vector

import gamecontrollerpoller
import ppap
from gamecontroller import GameController


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

    def grow_balls(self):
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

    def set_game_controller(self, game_controller: GameController):
        self._game_controller = game_controller

    def update_location(self):
        if self._orientation == self.VERTICAL_ORIENTATION:
            if self._game_controller.y_axis == gamecontrollerpoller.Y_AXIS_UP:
                self.center_y += self.LOCATION_UPDATE_AMOUNT
            elif self._game_controller.y_axis == gamecontrollerpoller.Y_AXIS_DOWN:
                self.center_y -= self.LOCATION_UPDATE_AMOUNT
        if self._orientation == self.HORIZONTAL_ORIENTATION:
            if self._game_controller.x_axis == gamecontrollerpoller.X_AXIS_LEFT:
                self.center_x -= self.LOCATION_UPDATE_AMOUNT
            elif self._game_controller.x_axis == gamecontrollerpoller.X_AXIS_RIGHT:
                self.center_x += self.LOCATION_UPDATE_AMOUNT

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

