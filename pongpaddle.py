from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ListProperty
)
from kivy.vector import Vector


class PongPaddle(Widget):
    rgba = ListProperty([0.75, 0.5, 0.5, 1])  # will be used as background color
    score = NumericProperty(0)
    current_ball_size = NumericProperty(0)
    READY_BALL_SIZE = 10
    HORIZONTAL_ORIENTATION = 0
    VERTICAL_ORIENTATION = 1

    _orientation = VERTICAL_ORIENTATION


    def grow_balls(self):
        if self.current_ball_size < self.READY_BALL_SIZE:
            self.current_ball_size += 1

    def get_spawned_ball(self):
        # todo: check to see if button is pressed, and if so release balls
        return None

    def set_paddle_orientation(self, orientation :int):
        self._orientation = orientation

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
                # todo: move the ball so it doesnt keep hitting the underside of the paddle
            else:
                offset_y = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                vel = bounced * 1.1
                ball.velocity = vel.x, vel.y + offset_y
                # todo: move the ball so it doesnt keep hitting the underside of the paddle
