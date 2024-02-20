import pygame
import sys
import random
from story import story
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((1000, 1000), RESIZABLE)
button_list = []

run = True
font_object = pygame.font.SysFont('your font', size=55)

index = 0
text_at_the_top = ''


def rect_border(rect, border_size):
    return pygame.Rect(rect.x - border_size, rect.y - border_size, rect.width + (2 * border_size),
                       rect.height + (2 * border_size))


def option_shuffler(story):
    for value in story:
        yield random.sample(value[1], len(value[1]))





def button_function(self):
    if self.visible:
        global index, run
        index_backup = index
        index = story[index][1][self.index][1]
        if index == index_backup:
            print(f"Turning the program off at index {index}")
            run = False
        try:
            set_text()
        except IndexError as error:
            print(f"Something is wrong with the file! (Index {index_backup})\n error: {error}")
            index = index_backup
            set_text()


def set_text():
    global text_at_the_top, index
    text_at_the_top = story[index][0]
    for i, button in enumerate(button_list):
        button.visible = True
        try:
            button.set_text(story[index][1][i][0])
        except IndexError:
            button.visible = False


class Button:
    def __init__(self, x, y, func=lambda self: None, text=""):
        self.index = len(button_list)
        button_list.append(self)
        self.x = x
        self.y = y
        self.func = func
        self.text = text
        self.rect = pygame.Rect(x, y, 300, 50)
        self.font = font_object.render(self.text, False, (255, 255, 255))
        self.held = False
        self.visible = True

    def draw(self):
        if not self.visible:
            return
        if self.held:
            pygame.draw.rect(screen, (0, 0, 200), self.rect)
        else:
            pygame.draw.rect(screen, (0, 0, 255), self.rect)

        screen.blit(self.font, self.font.get_rect(
            center=((self.rect.x + self.rect.width / 2), self.rect.y + (self.rect.height / 2))))

    def set_text(self, text):
        self.text = text
        self.font = font_object.render(text, False, (255, 255, 255))

    def update(self, event):
        if not self.visible:
            return
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.held = True
                return self.func(self)
        elif event.type == MOUSEBUTTONUP:
            self.held = False

    def destroy(self):
        button_list.remove(self)


for i in range(5):
    Button(50, 250 + (i * 60), func=button_function)

set_text()

while run:
    screen.fill((0, 255, 0))
    screen.blit(font_object.render(text_at_the_top, False, (0, 0, 0)), (0, 0))
    for button in button_list:
        button.draw()
    for event in pygame.event.get():
        for button in button_list:
            button.update(event)
        if event.type == QUIT:
            pygame.quit()
            run = False
            sys.exit()

    pygame.display.flip()
