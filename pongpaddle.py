from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty
)
from kivy.vector import Vector


class PongPaddle(Widget):
    score = NumericProperty(0)
    current_ball_size = NumericProperty(0)
    READY_BALL_SIZE = 10

    def grow_balls(self):
        if self.current_ball_size < self.READY_BALL_SIZE:
            self.current_ball_size += 1

    def get_spawned_ball(self):
        # todo: check to see if button is pressed, and if so release balls
        return None


    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset