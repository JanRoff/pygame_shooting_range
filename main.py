###################################################################################
# imports
###################################################################################

import random
import pygame
from pygame.locals import *


###################################################################################
# constants
###################################################################################

WIDTH = 1680
HEIGHT = 1050
TITLE = "Galaxy Shooter"
FPS = 40
MAXWIDTH = 1500
MINHEIGHT = 100
MAXHEIGHT = 800

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
RED = (255, 0, 0)

SCORE_FILE = "highscore.txt"

###################################################################################
# classes
###################################################################################

class Spaceship():
    def __init__(self, xpos:int, ypos:int):
        self.xpos = xpos
        self.ypos = ypos
        self.image = pygame.image.load("Assets/tie_jäger.png")
        self.rect = self.image.get_rect(topleft = (xpos, ypos))


class MovingTieFighter(Spaceship):
    def __init__(self, xpos:int, ypos:int, speed:int, direction:int):
        super().__init__(xpos, ypos)
        self.speed = speed
        self.direction = direction

    def move(self):
        self.xpos += self.speed * self.direction
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))
        

class StarDestroyer(Spaceship):
    def __init__(self, xpos:int, ypos:int, speed:int, direction:int, lives:int):
        super().__init__(xpos, ypos)
        self.speed = speed
        self.direction = direction
        self.lives = lives
        self.max_lives = lives
        if direction == 1:
            self.image = pygame.image.load("Assets/star_destroyer_right.png")
        else:
            self.image = pygame.image.load("Assets/star_destroyer_left.png")
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def move(self):
        self.xpos += self.speed * self.direction
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))


class Deathstar(Spaceship):
    def __init__(self, xpos:int, ypos:int, speed:int, direction:int, lives:int):
        super().__init__(xpos, ypos)
        self.speed = speed
        self.direction = direction
        self.lives = lives
        self.max_lives = lives
        self.image = pygame.image.load("Assets/deathstar.png")
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def move(self):
        self.xpos += self.speed * self.direction
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))

class Game:
    def __init__(self):
        # initialize game window, etc.
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.bg = pygame.image.load("Assets/background.jpg")
        self.dv = pygame.image.load("Assets/darth_vader.png")
        self.custom_cursor = pygame.image.load("Assets/crosshair.png")
        self.custom_cursor_rect = self.custom_cursor.get_rect()
        self.playing = True
        self.lives = 3
        self.score = 0
        self.round_counter = 0
        self.star_destroyer_count = 1
        self.tie_fighter_count = 10
        self.lives_ds = 50 # Deathstar lives
        self.topspeed = 3 # max speed of tie fighters
        self.game_over = False
        self.text_font = pygame.font.Font(None, 36)
        self.round_font = pygame.font.Font(None, 36)

        # set text fonts and sizes
        self.highscore_font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.restart_font = pygame.font.Font(None, 36)

        self.objects = []
        self.highscore = self.load_highscore()
        self.new()
        
    def new(self):
        self.round_counter += 1

        if self.round_counter % 30 == 0: # every 50th round
            xPos = random.choice([0, MAXWIDTH])
            if xPos == 0:
                direction = 1
            else:
                direction = -1
            speed = random.randint(1, 5)
            self.objects.append(Deathstar(xPos, 200, speed, direction, self.lives_ds))
            self.lives_ds += 50

        elif self.round_counter % 5 == 0: # every 5th round
            for i in range(self.star_destroyer_count):
                xPos = random.choice([0, MAXWIDTH])
                yPos = random.randint(MINHEIGHT, MAXHEIGHT)
                if xPos == 0:
                    direction = 1
                else:
                    direction = -1
                speed = random.randint(1, 5)
                self.objects.append(StarDestroyer(xPos, yPos, speed, direction, 5))
            self.star_destroyer_count += 1

        else:
            for i in range(self.tie_fighter_count):
                xPos = random.choice([0, MAXWIDTH])
                yPos = random.randint(MINHEIGHT, MAXHEIGHT)
                if xPos == 0:
                    direction = 1
                else:
                    direction = -1
                speed = random.randint(1, self.topspeed)
                self.objects.append(MovingTieFighter(xPos, yPos, speed, direction))

        if self.round_counter % 20 == 0:
            self.tie_fighter_count += 5
        if self.round_counter % 10 == 0:
            self.topspeed += 1
        return

    def run(self):
        # Game Loop
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            pygame.mouse.set_visible(False)  # disable cursor
            self.update_custom_cursor()  # update custom cursor


    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.playing = False
            if self.game_over == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in self.objects:
                        if i.rect.collidepoint(event.pos):
                            if isinstance(i, StarDestroyer) or isinstance(i, Deathstar):
                                i.lives -= 1
                                if i.lives == 0:
                                    self.score += 1
                                    self.objects.remove(i)
                        
                            else:
                                self.score += 1
                                self.objects.remove(i)

    def update(self):
        if self.game_over == False:
            for i in self.objects:
                i.move()
                if i.xpos > WIDTH or i.xpos < 0:
                    self.objects.remove(i)
                    self.lives -= 1
            if len(self.objects) == 0:
                self.new()   
    
    def draw(self):
        # Game Loop - draw
        self.screen.blit(self.bg, (0, 0))
        
        # draw "Score" - text
        score_text = self.text_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect(topright=(MAXWIDTH, 100))
        self.screen.blit(score_text, score_rect)

        # draw "Round" - text
        round_text = self.round_font.render("Round: " + str(self.round_counter), True, WHITE)
        round_rect = round_text.get_rect(topright=(MAXWIDTH, 130))
        self.screen.blit(round_text, round_rect)

        # draw "Highscore" - text
        highscore_text = self.highscore_font.render("Highscore: " + str(self.highscore), True, WHITE)
        highscore_rect = highscore_text.get_rect(topright=(MAXWIDTH, 160))
        self.screen.blit(highscore_text, highscore_rect)

        for i in range(self.lives):
            x = 100 + i * 100
            self.screen.blit(self.dv, (x, MINHEIGHT))

        if self.lives <= 0:
            self.game_over = True
            if self.score > self.highscore:  # check if new highscore is set
                self.highscore = self.score
                self.save_highscore()  # save new highscore

            # draw "Game Over" - text
            game_over_text = self.game_over_font.render("Game Over", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)

            # draw "Restart" - text
            restart_text = self.restart_font.render("Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            self.screen.blit(restart_text, restart_rect)

            mouse_pos = pygame.mouse.get_pos()
            if restart_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GREEN, restart_rect, border_radius=10)  # highlight the "Restart"-button when hovering over it
                if event.type == pygame.MOUSEBUTTONDOWN:
                        self.game_over = False
                        self.lives = 3
                        self.objects.clear()
                        self.round_counter = 0
                        self.score = 0
                        self.star_destroyer_count = 1
                        self.lives_ds = 50
                        self.topspeed = 3
                        self.tie_fighter_count = 10
                        self.new()
        for i in self.objects:
            if isinstance(i, StarDestroyer) or isinstance(i, Deathstar):
                self.draw_health_bar(i)
            self.screen.blit(i.image, i.rect)

        self.screen.blit(self.custom_cursor, self.custom_cursor_rect) # draw custom cursor
        pygame.display.update()

    def draw_health_bar(self, object):
        health_bar_width = 100
        health_bar_height = 10
        health_bar_x = object.rect.x
        health_bar_y = object.rect.y - health_bar_height - 5
        pygame.draw.rect(self.screen, GREEN, (health_bar_x, health_bar_y, health_bar_width, health_bar_height)) # draw healthbar
        remaining_health = max(0, (object.lives / object.max_lives) * health_bar_width) # get remaining health
        pygame.draw.rect(self.screen, RED, (health_bar_x, health_bar_y, remaining_health, health_bar_height)) # draw remaining health
        return

    def update_custom_cursor(self):
        # Updating the current position of the custom cursor
        mouse_pos = pygame.mouse.get_pos()
        self.custom_cursor_rect.center = mouse_pos
        return
    
    def save_highscore(self):
        # write highscore in file
        with open(SCORE_FILE, "w") as file:
            file.write(str(self.highscore))

    def load_highscore(self):
        # load highscore from file
        try:
            with open(SCORE_FILE, "r") as file:
                highscore = int(file.read())
                return highscore
        except FileNotFoundError:
            return 0


###################################################################################
# main program
###################################################################################

g = Game()
while g.playing:
    g.run()

pygame.quit()
