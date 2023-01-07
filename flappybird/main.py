from random import randint
import time
from classes import *
from pathlib import Path

import pygame

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()

PATH = str(Path(__file__).parent) + "\media"

FPS = 30
WIDTH = 1920 // 2
HEIGHT = 1080 // 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))

BACKGROUND_LOOPING_POINT = 413
background = pygame.image.load(f'{PATH}\\background.png')
background = pygame.transform.scale(background, (1652, HEIGHT))
BG_SPEED = 1
BG_POS = 0

GROUND_LOOPING_POINT = 100
ground = pygame.image.load(f'{PATH}\\ground.png')
ground_dims = (1100, 16)
ground = pygame.transform.scale(ground, ground_dims)
GRD_SPEED = 3
GRD_POS = 0

bird_sprite = pygame.image.load(f'{PATH}\\bird.png')
bird_dims = (WIDTH // 20, int(24 / 38 * WIDTH // 20))
bird_sprite = pygame.transform.scale(bird_sprite, bird_dims)

bird = Bird(WIDTH // 2 - bird_dims[0] // 2, HEIGHT // 2 - bird_dims[1] // 2, bird_dims[0], bird_dims[1])
G_CONSTANT = 1.5
JUMP = 18

INITIAL_PIPE_SPEED = 4
PIPE_SPEED = INITIAL_PIPE_SPEED
INITIAL_PIPE_INTERVAL = 200
PIPE_INTERVAL = INITIAL_PIPE_INTERVAL  # Distance between pipe pairs
PIPE_DISTANCE = 180  # Distance between pipes for bird to fit through
pipe_sprite = pygame.image.load(f'{PATH}\\pipe.png')
pipe_dims = (WIDTH//10, int(HEIGHT/1.6))
b_pipe_sprite = pygame.transform.scale(pipe_sprite, pipe_dims)
t_pipe_sprite = pygame.transform.flip(b_pipe_sprite, False, True)

MAX_PAIRS = int(WIDTH/pipe_dims[0]) + 2

ALLOWED = {"_", "-", " ", "@", "<", ">", ",", ".", "/"}

def initialisePairs():
    pipe_y = randint(HEIGHT - pipe_dims[1], HEIGHT - pipe_dims[1] + 200)
    bottomPipe = Pipe(WIDTH, pipe_y, pipe_dims[0], pipe_dims[1], True)
    # Position top pipe based on top of bottom pipe
    topPipe = Pipe(WIDTH, pipe_y - PIPE_DISTANCE - pipe_dims[1], pipe_dims[0], pipe_dims[1], False)
    pipePair = PipePair(topPipe, bottomPipe, PIPE_DISTANCE)
    # Define a list with 5 pipe pairs
    pipePairs = [pipePair]
    pairIndex = 0  # Tracks right most pipe
    return pipePairs, pairIndex, pipe_y

COLOUR = (255, 255, 255)

flappy_font = f"{PATH}\\flappy.ttf"
other_font = f"{PATH}\\font.ttf"

score_sound = pygame.mixer.Sound(f"{PATH}\\bird12_score.wav")
jump_sound = pygame.mixer.Sound(f"{PATH}\\bird12_jump.wav")
explosion_sound = pygame.mixer.Sound(f"{PATH}\\bird12_explosion.wav")
pygame.mixer.music.load(f"{PATH}\\bird12_marios_way.mp3")
pygame.mixer.music.play(-1)


def drawFont(text, font_type, size, location):
    font = pygame.font.Font(font_type, size)
    word = font.render(text, True, COLOUR)
    word_rect = word.get_rect(center=location)
    screen.blit(word, word_rect)

leeway = 10


def collide(body1, body2):  # Standard AABB collision
    if (body1.x + leeway < body2.x + body2.width and
            body1.x + body1.width > body2.x + leeway and
            body1.y + leeway < body2.y + body2.height and
            body1.y + body1.height > body2.y + leeway):
        return True
    return False

def addScore(highscores, score):
    for i, row in enumerate(highscores):
        if score[1] >= row[1]:
            highscores.insert(i, score)
            break
    highscores.pop()
    return highscores

def getFontSize(s):
    if len(s) > 30:
        return 20
    elif len(s) > 20:
        return 30
    else:
        return 40
    
def drawGridLines():
    pygame.draw.rect(screen, COLOUR, pygame.Rect(200, 110, 5, 410))
    pygame.draw.rect(screen, COLOUR, pygame.Rect(740, 110, 5, 410))
    for i in range(5):
        pygame.draw.rect(screen, COLOUR, pygame.Rect(40, 170 + i * 70, WIDTH - 80, 5))

def redrawGameWindow(bg_pos, grd_pos, t):
    screen.blit(background, (BG_POS, 0))
    screen.blit(ground, (GRD_POS, HEIGHT - ground_dims[1]))
    if state == "start":
        screen.blit(bird_sprite, (bird.x, bird.y))
        drawFont("FLAPPY", flappy_font, 100, (WIDTH // 2, 100))
        drawFont("Press 'Enter' to begin!", flappy_font, 50, (WIDTH // 2, HEIGHT - 200))
    if state == "ready":
        time_elapsed = t * (0 < t < 4) + 1 * (t >= 4 or t < 0)  # Fix bug with timer
        drawFont(f"{int(4 - time_elapsed)}", other_font, 400, (WIDTH // 2, HEIGHT // 2))

    if state == "play":
        screen.blit(bird_sprite, (bird.x, bird.y))
        drawFont(f"{SCORE}", flappy_font, 50, (WIDTH//2, 50))
        for pair in pipePairs:
            screen.blit(t_pipe_sprite, (pair.top.x, pair.top.y))
            screen.blit(b_pipe_sprite, (pair.bottom.x, pair.bottom.y))
            pair.top.x -= PIPE_SPEED
            pair.bottom.x -= PIPE_SPEED
            
    if state == "name":
        drawFont(f"Congratulations! Your score is:", flappy_font, 50, (WIDTH//2, 50))
        drawFont(f"{SCORE}", flappy_font, 150, (WIDTH//2, 150))
        drawFont("Enter your name:", flappy_font, 40, (WIDTH//2, HEIGHT//2 - 10))
        drawFont(NAME, flappy_font, 100, (WIDTH//2, HEIGHT//2 + 80))
        drawFont("Press 'Enter' to continue!", flappy_font, 30, (WIDTH//2, HEIGHT//2 + 180))
        
    if state == "board":
        drawFont("HALL OF FAME", flappy_font, 80, (WIDTH//2, 60))
        drawFont("RANK", flappy_font, 50, (120, 140))
        drawFont("NAME", flappy_font, 50, (WIDTH//2, 140))
        drawFont("SCORE", flappy_font, 50, (840, 140))
        drawGridLines()
        for i in range(5):
            height = 205 + i * 70
            drawFont(f"#{i+1}", flappy_font, 40, (100, height))
            drawFont(HIGHSCORES[i][0], flappy_font, getFontSize(HIGHSCORES[i][0]), (WIDTH//2, height))
            drawFont(str(HIGHSCORES[i][1]), flappy_font, 40, (840, height))
        

    if state == "end":
        drawFont("SCORE:", flappy_font, 50, (WIDTH//2, 100))
        drawFont(f"{SCORE}", flappy_font, 200, (WIDTH//2, HEIGHT//2))
        drawFont("Press 'Enter' to restart!", flappy_font, 50, (WIDTH//2, HEIGHT - 100))

    bg_pos -= BG_SPEED
    bg_pos %= -BACKGROUND_LOOPING_POINT
    grd_pos -= GRD_SPEED
    grd_pos %= -GROUND_LOOPING_POINT

    pygame.display.update()

    return bg_pos, grd_pos

def load():
    highscores = []
    with open(str(Path(__file__).parent) + "\highscores.txt", "r") as txt_file:
        for row in txt_file:
            if row == "\n": break
            row = str(row).strip("\n").split(",")
            highscores.append([row[0], int(row[1])])
    
    return highscores

def write(highscores):
    with open(str(Path(__file__).parent) + "\highscores.txt", "w") as txt_file:
        for name, score in highscores:
            txt_file.write(f"{name},{score}\n")

run = True
state = "start"
t0 = 0
t1 = 0
isJump = False
SCORE = 0
HIGHSCORES = load()
MIN_HIGHSCORE = 5
NAME = ""
while run:
    screen.fill((0, 0, 0))
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == "play":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                isJump = True
        if state == "name":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if NAME:
                        NAME = NAME[:-1]
                elif event.unicode in ALLOWED or event.unicode.isalnum():
                    NAME += event.unicode   
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN and NAME:
                    HIGHSCORES = addScore(HIGHSCORES, [NAME, SCORE])
                    NAME = ""
                    state = "board"
                

    if state == "start":
        pipePairs, pairIndex, pipe_y = initialisePairs()
        SCORE = 0
        bird.x = WIDTH // 2 - bird_dims[0] // 2
        bird.y = HEIGHT // 2 - bird_dims[1] // 2
        bird.velocity = 0
        SCORE = 0
        PIPE_SPEED = INITIAL_PIPE_SPEED
        PIPE_INTERVAL = INITIAL_PIPE_INTERVAL
        if keys[pygame.K_RETURN]:
            t0 = time.time()
            state = "ready"

    elif state == "ready":
        bird.x = WIDTH // 3 - bird_dims[0] // 2
        t1 = time.time()
        if t1 - t0 >= 2.9:
            state = "play"

    if state == "play":
        # Increase difficulty of game as it progresses
        PIPE_INTERVAL = max(INITIAL_PIPE_INTERVAL - 5 * (SCORE // 5), 140)
        PIPE_SPEED = min(INITIAL_PIPE_SPEED + 0.5 * (SCORE // 5), 6)

        # Bird jump logic
        if isJump:
            pygame.mixer.Sound.play(jump_sound)
            isJump = True
            Bird.jump(bird, JUMP)

        isJump = False

        bird.velocity += G_CONSTANT
        bird.y += bird.velocity

        if bird.y < 0 or bird.y > HEIGHT - bird_dims[1]:
            pygame.mixer.Sound.play(explosion_sound)
            if SCORE >= max(HIGHSCORES[-1][1], MIN_HIGHSCORE):                        
                state = "name"
            else:
                state = "end"

        # Pipe creation logic
        if pipePairs[pairIndex].top.x + pipe_dims[0] + PIPE_INTERVAL <= WIDTH:  # Check if new pipe needs to be created
            pairIndex = (pairIndex + 1) % MAX_PAIRS

            # Determine height of new pipe
            pipe_y += randint(-100, 100)
            if pipe_y < HEIGHT - pipe_dims[1]:  # Ensure complete rendering of bottom pipe
                pipe_y = HEIGHT - pipe_dims[1]
            elif pipe_y - PIPE_DISTANCE - pipe_dims[1] > 0:  # Ensure complete rendering of top pipe
                pipe_y = PIPE_DISTANCE + pipe_dims[1]

            newBottom = Pipe(WIDTH, pipe_y, pipe_dims[0], pipe_dims[1], True)
            newTop = Pipe(WIDTH, pipe_y - PIPE_DISTANCE - pipe_dims[1], pipe_dims[0], pipe_dims[1], False)
            newPair = PipePair(newTop, newBottom, PIPE_DISTANCE)

            # Add new pipe pair
            if pairIndex > len(pipePairs) - 1:
                pipePairs.append(newPair)
            else:
                del pipePairs[pairIndex]  # Prevent memory loss
                pipePairs[pairIndex] = newPair

        for pair in pipePairs:
            if pair.top.x <= bird.x:
                if not pair.top.check:
                    pair.top.check = True
                    SCORE += 1
                    pygame.mixer.Sound.play(score_sound)

            if pair.top.x < WIDTH // 3 + bird_dims[0]:
                if collide(pair.top, bird) or collide(pair.bottom, bird):
                    # go to name or end based on score
                    pygame.mixer.Sound.play(explosion_sound)
                    if SCORE >= max(HIGHSCORES[-1][1], MIN_HIGHSCORE):                        
                        state = "name"
                    else:
                        state = "end"
    
    if state == "board":
        while state == "board":
            clock.tick(FPS)
            BG_POS, GRD_POS = redrawGameWindow(BG_POS, GRD_POS, t1 - t0)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    state = "start"
                    run = False
                    break
                if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                    state = "start"
                    break
    
    if state == "end":
        while state == "end":
            clock.tick(FPS)
            BG_POS, GRD_POS = redrawGameWindow(BG_POS, GRD_POS, t1 - t0)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    state = "board"
                    run = False
                    break
                if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                    state = "board"
                    break

    BG_POS, GRD_POS = redrawGameWindow(BG_POS, GRD_POS, t1 - t0)

pygame.quit()
write(HIGHSCORES)