########################################################
PLAYER1_ID: int = 1
PLAYER2_ID: int = 2
PLAYER3_ID: int = 3
PLAYER4_ID: int = 4


def get_player_id_desc(player_id: int) -> str:
    if player_id is None:
        return 'None'
    elif player_id == PLAYER1_ID:
        return 'p1'
    elif player_id == PLAYER2_ID:
        return 'p2'
    elif player_id == PLAYER3_ID:
        return 'p3'
    elif player_id == PLAYER4_ID:
        return 'p4'


########################################################
HORIZ_LEFT = -1
HORIZ_MIDDLE = 0
HORIZ_RIGHT = 1

VERT_TOP = 1
VERT_MIDDLE = 0
VERT_BOTTOM = -1

REGION_LT = 0
REGION_LM = 1
REGION_LB = 2
REGION_MT = 3
REGION_MM = 4
REGION_MB = 5
REGION_RT = 6
REGION_RM = 7
REGION_RB = 8

PADDLE_FACE_DIRECTION_RIGHT = PLAYER1_ID
PADDLE_FACE_DIRECTION_BOTTOM = PLAYER2_ID
PADDLE_FACE_DIRECTION_LEFT = PLAYER3_ID
PADDLE_FACE_DIRECTION_TOP = PLAYER4_ID

########################################################
X_AXIS_LEFT = -1
X_AXIS_MIDDLE = 0
X_AXIS_RIGHT = 1

Y_AXIS_UP = 1
Y_AXIS_MIDDLE = 0
Y_AXIS_DOWN = -1




