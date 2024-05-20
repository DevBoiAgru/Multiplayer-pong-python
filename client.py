import socket, pygame, pickle, time, sys
from _thread import *
import network

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((sys.argv[1], int(sys.argv[2])))

events: list[network.NetworkEvent] = []

WIDTH: int = None
HEIGHT: int = None
FPS: int = None
PLAYER_INDEX: int = None
READY = False                           # False untill the server sends the join event

def recieveEvents(s: socket.socket):
    """Recieves events from the server and handles them for some events like joining the game"""
    global WIDTH, HEIGHT, PLAYER_INDEX, FPS, READY
    while True:
        try:
            eventData = s.recv(1024)
            event: network.NetworkEvent = pickle.loads(eventData)

            if event.type == network.EVENT_PR_JOIN:
                PLAYER_INDEX = event.data.get("i")
                WIDTH = event.data.get("w")
                HEIGHT = event.data.get("h")
                FPS = event.data.get("f")
                READY = True
            elif event.type == network.EVENT_REG_UPDATE:
                events.append(event)
        except pickle.UnpicklingError:
            pass
        except socket.error as err:
            # Client disconnected
            break

start_new_thread(recieveEvents, (sock,))

while not READY:                           # Wait for the server join event
    time.sleep(0.5)

# Init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer pong. Player:", str(PLAYER_INDEX))
font = pygame.font.Font(pygame.font.get_default_font(), 52)
clock = pygame.time.Clock()

paddle1 = pygame.Rect(0, 0, 0, 0)
paddle2 = pygame.Rect(0, 0, 0, 0)
ballCoords: list = [WIDTH//2, HEIGHT//2]                                   # Coords of the ball
scores = [0, 0]

while True:
    for event in events:
        if event.type == network.EVENT_REG_UPDATE:
            paddle1 = pygame.Rect(*event.data.get("p1"))
            paddle2 = pygame.Rect(*event.data.get("p2"))
            ballCoords = event.data.get("b")
            scores = event.data.get("s")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Send input event to the server
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            inputEvent = network.NetworkEvent(network.EVENT_REG_INPUT, {"i": PLAYER_INDEX, "a": 0})         # i is playerindex, a is action.
            sock.send(pickle.dumps(inputEvent))
        elif keys[pygame.K_w]:                                                                              # action 1 is up, 0 is down
            inputEvent = network.NetworkEvent(network.EVENT_REG_INPUT, {"i": PLAYER_INDEX, "a": 1})
            sock.send(pickle.dumps(inputEvent))
    screen.fill((0,0,0))

    # Draw score
    scoreText = font.render(f"{scores[0]} | {scores[1]}", True, (255, 255, 255))
    scoreTextRect = scoreText.get_rect(center=(WIDTH/2, 50))
    screen.blit(scoreText, scoreTextRect)

    # Draw assets
    pygame.draw.rect(screen, (255, 255, 255), paddle1)
    pygame.draw.rect(screen, (255, 255, 255), paddle2)
    pygame.draw.circle(screen, (255, 255, 255), (ballCoords[0], ballCoords[1]), 10)

    pygame.display.update()
    clock.tick(FPS)