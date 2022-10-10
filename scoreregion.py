from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector


class ScoreRegion(Widget):
    score = NumericProperty(0)

    _paddle = None

    def set_paddle(self, paddle):
        self._paddle = paddle

#    def check_for_score(self, ball):
#        if self.collide_widget(ball):
#            b_paddle = ball.get_bounced_paddle()
#            if b_paddle is not None:
#                b_paddle.score += 1
#            #self._paddle.score += 1
#            return True
#        else:
#            return False
