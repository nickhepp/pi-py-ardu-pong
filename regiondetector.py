from location import Location
from screenbounds import ScreenBounds

class RegionDetector:
    def __init__(self):
        self.HORIZ_LEFT = -1
        self.HORIZ_MIDDLE = 0
        self.HORIZ_RIGHT = 1

        self.VERT_TOP = 1
        self.VERT_MIDDLE = 0
        self.VERT_BOTTOM = -1

        self.REGION_LT = 0
        self.REGION_LM = 1
        self.REGION_LB = 2
        self.REGION_MT = 3
        self.REGION_MM = 4
        self.REGION_MB = 5
        self.REGION_RT = 6
        self.REGION_RM = 7
        self.REGION_RB = 8

    def get_region(self, screen_bounds: ScreenBounds, ball_location: Location):

        is_horiz_left = is_horiz_mid = is_horiz_right = False
        is_vert_top = is_vert_mid = is_vert_bottom = False

        if ball_location.x < screen_bounds.left:
            is_horiz_left = True
        elif screen_bounds.left <= ball_location.x <= screen_bounds.right:
            is_horiz_mid = True
        else:
            is_horiz_right = True

        if ball_location.y < screen_bounds.bottom:
            is_vert_bottom = True
        elif screen_bounds.bottom <= ball_location.y <= screen_bounds.top:
            is_vert_mid = True
        else:
            is_vert_top = True

        region = self.REGION_LT
        if is_horiz_left and is_vert_top:
            region = self.REGION_LT
        elif is_horiz_left and is_vert_mid:
            region = self.REGION_LM
        elif is_horiz_left and is_vert_bottom:
            region = self.REGION_LB
        elif is_horiz_mid and is_vert_top:
            region = self.REGION_MT
        elif is_horiz_mid and is_vert_mid:
            region = self.REGION_MM
        elif is_horiz_mid and is_vert_bottom:
            region = self.REGION_MB
        elif is_horiz_right and is_vert_top:
            region = self.REGION_RT
        elif is_horiz_right and is_vert_mid:
            region = self.REGION_RM
        else:  # if is_horiz_right and is_vert_bottom:
            region = self.REGION_RB

        return region
