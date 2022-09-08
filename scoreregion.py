from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector


class ScoreRegion(Widget):
    score = NumericProperty(0)
