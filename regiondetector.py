from location import Location
from screenbounds import ScreenBounds
import ppap




class RegionDetector:

    def get_scored_on_player_from_ball_location(self,
                                                region: int,
                                                screen_bounds: ScreenBounds,
                                                ball_location: Location):
        player_id: int
        if region == ppap.REGION_LM:
            player_id = ppap.PLAYER1_ID
        elif region == ppap.REGION_LT:
            if abs(screen_bounds.left - ball_location.x) < abs(ball_location.y - screen_bounds.top):
                player_id = ppap.PLAYER2_ID
            else:
                player_id = ppap.PLAYER2_ID
        elif region == ppap.REGION_MT:
            player_id = ppap.PLAYER2_ID
        elif region == ppap.REGION_RT:
            if abs(ball_location.x - screen_bounds.right) < abs(ball_location.y - screen_bounds.top):
                player_id = ppap.PLAYER2_ID
            else:
                player_id = ppap.PLAYER3_ID
        elif region == ppap.REGION_RM:
            player_id = ppap.PLAYER3_ID
        elif region == ppap.REGION_RB:
            if abs(ball_location.x - screen_bounds.right) < abs(screen_bounds.bottom - ball_location.y):
                player_id = ppap.PLAYER4_ID
            else:
                player_id = ppap.PLAYER3_ID
        elif region == ppap.REGION_MB:
            player_id = ppap.PLAYER4_ID
        elif region == ppap.REGION_LB:
            if abs(screen_bounds.left - ball_location.x) < abs(screen_bounds.bottom - ball_location.y):
                player_id = ppap.PLAYER4_ID
            else:
                player_id = ppap.PLAYER3_ID
        else:  # if region == ppap.REGION_MM:
            player_id = None

        return player_id


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

        region = ppap.REGION_LT
        if is_horiz_left and is_vert_top:
            region = ppap.REGION_LT
        elif is_horiz_left and is_vert_mid:
            region = ppap.REGION_LM
        elif is_horiz_left and is_vert_bottom:
            region = ppap.REGION_LB
        elif is_horiz_mid and is_vert_top:
            region = ppap.REGION_MT
        elif is_horiz_mid and is_vert_mid:
            region = ppap.REGION_MM
        elif is_horiz_mid and is_vert_bottom:
            region = ppap.REGION_MB
        elif is_horiz_right and is_vert_top:
            region = ppap.REGION_RT
        elif is_horiz_right and is_vert_mid:
            region = ppap.REGION_RM
        else:  # if is_horiz_right and is_vert_bottom:
            region = ppap.REGION_RB

        return region
