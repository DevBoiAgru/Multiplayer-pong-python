class Rect:
    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float
    centerx: float
    centery: float

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
FPS                     = 60
WIDTH                   = 1080                                     # Screen width
HEIGHT                  = 720                                      # Screen height
PADDLE_HEIGHT           = 100
PADDLE_WIDTH            = 10
PADDLE_SPEED            = 400
PADDLE_OFFSET           = 20                                       # Distance of the paddles from the edge of the screen
PADDLE_Y_RESTITUTION    = 100                                      # Velocity scalar in the y direction added by the paddle when it hits the ball
COLLISION_BUFFER        = 2                                        # Margin so that collision doesnt get things stuck
BALL_INITIAL_XVEL, BALL_INITIAL_YVEL = 350.0, 0.0                  # Initial X and Y velocities for the ball
BALL_INITIAL_X, BALL_INITIAL_Y = WIDTH // 2, HEIGHT // 2           # Initial X and Y positions for the ball
BALL_RADIUS = 10
PYGAME = False                                                     # Set true for pygame to be enabled
RECT_CLASS = Rect                                                  # Rect class. Can be changed to pygame.rect for pygame compatibillity


# Pygame initialization
if PYGAME:
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()
    RECT_CLASS = pygame.Rect
else:
    import time

# Assets and utilities
paddle1 = RECT_CLASS(PADDLE_OFFSET - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = RECT_CLASS(WIDTH - PADDLE_OFFSET, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ballCoords: list[int, int] = [BALL_INITIAL_X, BALL_INITIAL_Y]
ballVel: list[float, float] = [BALL_INITIAL_XVEL, BALL_INITIAL_YVEL]
scores: list[int] = [0, 0]


# Game loop
running = True
dt: float = 1/FPS if not PYGAME else None
while running:
    if PYGAME:
        dt: float = clock.tick(FPS)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()

        # Keyboard input
        keys = pygame.key.get_pressed()
        
        # Only move if paddles are within screen bounds
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.move_ip(0, PADDLE_SPEED * dt)
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.move_ip(0, PADDLE_SPEED * dt * (-1))

        if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
            paddle2.move_ip(0, PADDLE_SPEED * dt)
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.move_ip(0, PADDLE_SPEED * dt * (-1))

        screen.fill((0, 0, 0))
    else:
        time.sleep(dt)

    # Check if ball is colliding with the horizontal edges of the screen
    if ballCoords[1] > (HEIGHT - BALL_RADIUS) or ballCoords[1] < BALL_RADIUS:
        ballVel[1] = ballVel[1] * (-1)

    # Check if ball is colliding with the vertical edges of the screen
    if ballCoords[0] < BALL_RADIUS:             # Left side
        scores[1] += 1
        # Reset ball
        ballCoords = [BALL_INITIAL_X, BALL_INITIAL_Y]
        ballVel = [BALL_INITIAL_XVEL * (-1) if scores[0] > scores[1] else BALL_INITIAL_XVEL,    # Opposite velocity if score is higher on either side
                BALL_INITIAL_YVEL]
    if ballCoords[0] > (WIDTH - BALL_RADIUS):   # Right side
        scores[0] += 1
        # Reset ball
        ballCoords = [BALL_INITIAL_X, BALL_INITIAL_Y]
        ballVel = [BALL_INITIAL_XVEL * (-1) if scores[0] > scores[1] else BALL_INITIAL_XVEL,    # Opposite velocity if score is higher on either side
                BALL_INITIAL_YVEL]

    # Check if ball collides with a paddle
    if ((ballCoords[0] - BALL_RADIUS) < paddle1.right or             # Left paddle
        (ballCoords[0] + BALL_RADIUS) > paddle2.left):               # Right paddle

        if (ballCoords[0] - BALL_RADIUS) < paddle1.right:
            hitPaddle = paddle1
        else:
            hitPaddle = paddle2
        
        # Check if ball is within the paddle. If it is, then only continue
        if ballCoords[1] > hitPaddle.top and ballCoords[1] < hitPaddle.bottom:

            ballVel[0] = ballVel[0] * (-1)
            
            # Y position of ball relative to paddle center (normalised between -1 and 1)
            relativeY: int = (ballCoords[1] - hitPaddle.centery) / (hitPaddle.height / 2)
            ballVel[1] = relativeY * PADDLE_Y_RESTITUTION


    # Update ball position
    ballCoords[0] += ballVel[0] * dt
    ballCoords[1] += ballVel[1] * dt

    if PYGAME:
        pygame.draw.rect(screen, (255, 255, 255), paddle1)
        pygame.draw.rect(screen, (255, 255, 255), paddle2)
        pygame.draw.circle(screen, (255, 255, 255), ballCoords, BALL_RADIUS)
        pygame.display.update()