import socket, time, pickle, network
from _thread import start_new_thread

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((network.IP, network.PORT))
sock.listen(1)

# GAME
class Rect:
    def __init__(self, left: float, top: float, width: float, height: float) -> None:
        self.update(left, top, width, height)

    def move_ip(self, x: float, y: float) -> None:
        self.update(self.left + x, self.top + y, self.width, self.height)

    def update(self, left: float, top: float, width: float, height: float) -> None:
        self.left = left
        self.right = left + width
        self.bottom = top + height
        self.top = top
        self.width = width
        self.height = height
        self.centerx = left + width / 2
        self.centery = top + height / 2

# Constants
FPS = 90
WIDTH = 1080  # Screen width
HEIGHT = 720  # Screen height
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 10
PADDLE_SPEED = 800
PADDLE_OFFSET = 20  # Distance of the paddles from the edge of the screen
PADDLE_Y_RESTITUTION = 100  # Velocity scalar in the y direction added by the paddle when it hits the ball
COLLISION_BUFFER = 2  # Margin so that collision doesnt get things stuck
BALL_INITIAL_XVEL, BALL_INITIAL_YVEL = 550.0, 0.0  # Initial X and Y velocities for the ball
BALL_INITIAL_X, BALL_INITIAL_Y = WIDTH // 2, HEIGHT // 2  # Initial X and Y positions for the ball
BALL_RADIUS = 10
RECT_CLASS = Rect

# Assets and utilities
paddle1 = RECT_CLASS(PADDLE_OFFSET - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = RECT_CLASS(WIDTH - PADDLE_OFFSET, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ballCoords = [BALL_INITIAL_X, BALL_INITIAL_Y]
ballVel = [BALL_INITIAL_XVEL, BALL_INITIAL_YVEL]
scores = [0, 0]
running = True
dt = 1 / FPS

# Networking
connections = []
events = []

def receiveEvents(sock: socket.socket):
    global events
    while True:
        try:
            data = sock.recv(1024)
            events.append(pickle.loads(data))
        except socket.error as err:
            # Client disconnected (maybe) so stop checking for messages
            break

# Keep accepting connections until the game is full (i.e 2 players)
while len(connections) < 2:
    client, addr = sock.accept()
    
    # When client joins, send them a join event with their index and add them to the connections list
    joinData = {"i": len(connections), "w": WIDTH, "h": HEIGHT, "f": FPS}
    joinEvent = network.NetworkEvent(network.EVENT_PR_JOIN, joinData)
    client.send(pickle.dumps(joinEvent))

    connections.append(client)
    start_new_thread(receiveEvents, (client, ))  # Start checking for events from every client
    time.sleep(1)  # Cooldown before accepting new connections or trying to connect again

while running:
    for event in events:
        if event.type == network.EVENT_REG_INPUT:
            player = event.data.get("i")  # i is playerindex, a is action. action 1 is up, 0 is down
            paddle = paddle1 if player == 0 else paddle2
            if event.data.get("a") == 1 and paddle.top > 0:
                paddle.move_ip(0, PADDLE_SPEED * dt * (-1))
            elif event.data.get("a") == 0 and paddle.bottom < HEIGHT:
                paddle.move_ip(0, PADDLE_SPEED * dt * (1))
        events.remove(event)

    # Check if ball is colliding with the horizontal edges of the screen
    if ballCoords[1] > (HEIGHT - BALL_RADIUS) or ballCoords[1] < BALL_RADIUS:
        ballVel[1] = ballVel[1] * (-1)

    # Check if ball is colliding with the vertical edges of the screen
    if ballCoords[0] < BALL_RADIUS:  # Left side
        scores[1] += 1
        # Reset ball
        ballCoords = [BALL_INITIAL_X, BALL_INITIAL_Y]
        ballVel = [BALL_INITIAL_XVEL * (-1) if scores[0] > scores[1] else BALL_INITIAL_XVEL,  # Opposite velocity if score is higher on either side
                   BALL_INITIAL_YVEL]
    if ballCoords[0] > (WIDTH - BALL_RADIUS):  # Right side
        scores[0] += 1
        # Reset ball
        ballCoords = [BALL_INITIAL_X, BALL_INITIAL_Y]
        ballVel = [BALL_INITIAL_XVEL * (-1) if scores[0] > scores[1] else BALL_INITIAL_XVEL,  # Opposite velocity if score is higher on either side
                   BALL_INITIAL_YVEL]

    # Check if ball collides with a paddle
    if ((ballCoords[0] - BALL_RADIUS) < paddle1.right or  # Left paddle
            (ballCoords[0] + BALL_RADIUS) > paddle2.left):  # Right paddle

        if (ballCoords[0] - BALL_RADIUS) < paddle1.right:
            hitPaddle = paddle1
        else:
            hitPaddle = paddle2

        # Check if ball is within the paddle. If it is, then only continue
        if ballCoords[1] > hitPaddle.top and ballCoords[1] < hitPaddle.bottom:
            ballVel[0] = ballVel[0] * (-1)
            
            # Y position of ball relative to paddle center (normalised between -1 and 1)
            relativeY = (ballCoords[1] - hitPaddle.centery) / (hitPaddle.height / 2)
            ballVel[1] = relativeY * PADDLE_Y_RESTITUTION

    # Update ball position
    ballCoords[0] += ballVel[0] * dt
    ballCoords[1] += ballVel[1] * dt

    # Create an event to send to all players with the current game state
    gameData = {
        "b": ballCoords,
        "s": scores,
        "p1": [paddle1.left, paddle1.top, paddle1.width, paddle1.height],
        "p2": [paddle2.left, paddle2.top, paddle2.width, paddle2.height]
    }
    updateEvent = network.NetworkEvent(network.EVENT_REG_UPDATE, gameData)
    for player in connections:
        try:
            player.send(pickle.dumps(updateEvent))
        except socket.error as err:
            print("Socket error", err)
            print("\nA client left the game")
            exit()
    time.sleep(1 / FPS)

sock.close()
