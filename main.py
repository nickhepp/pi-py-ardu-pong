import pongball, pongpaddle, scoreregion
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import random


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
        self.player1.set_paddle_orientation(self.VERTICAL_ORIENTATION)
        self.region1.set_paddle(self.player1)

        self.player2.set_paddle_orientation(self.VERTICAL_ORIENTATION)
        self.region2.set_paddle(self.player2)

        self.player3.set_paddle_orientation(self.HORIZONTAL_ORIENTATION)
        self.region3.set_paddle(self.player3)

        self.player4.set_paddle_orientation(self.HORIZONTAL_ORIENTATION)
        self.region4.set_paddle(self.player4)


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
            rand_val : int = random.randint(0, 3)
            if rand_val == 0:
                self.serve_ball(vel=(4, 0))
            elif rand_val == 1:
                self.serve_ball(vel=(-4, 0))
            elif rand_val == 2:
                self.serve_ball(vel=(0, 4))
            else: # 3
                self.serve_ball(vel=(0, -4))


        #if self.ball.x < self.x:
        #    self.player2.score += 1

        #if self.ball.right > self.width:
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
        return game


if __name__ == '__main__':
    PongApp().run()
