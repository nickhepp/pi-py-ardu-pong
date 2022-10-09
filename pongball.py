from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty
from kivy.vector import Vector

class PongBall(Widget):
    rgba = ListProperty([0.5, 0.5, 0.5, 1])  # will be used as background color

    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    # referencelist property so we can use ball.velocity as
    # a shorthand, just like e.g. w.pos for w.x and w.y
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    _bounced_paddle = None

    initialized = False

    # ``move`` function will move the ball one step. This
    #  will be called in equal intervals to animate the ball
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def set_bounced_paddle(self, bounced_paddle):
        self._bounced_paddle = bounced_paddle

    def get_bounced_paddle(self):
        return self._bounced_paddle
