import time
import pygame
import sys
import random
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((1000, 1000), RESIZABLE)
button_list = []
story = []

run = False
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
        self.rect = pygame.Rect(x, y, 400, 50)
        self.font = font_object.render(self.text, False, (255, 255, 255))
        self.color_inactive = (0, 0, 200)
        self.color_active = (0, 0, 255)
        self.held = False
        self.visible = True

    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(screen, (0, 0, 0), self.rect)
        if self.held:
            pygame.draw.rect(screen, self.color_active, rect_border(self.rect, -4))
        else:
            pygame.draw.rect(screen, self.color_inactive, rect_border(self.rect, -4))


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
        del self


class InputText:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 350, 50)
        self.text = ''
        self.del_bool = False
        self.del_time = time.time()
        self.button = Button(x - 48, y)
        self.button.destroy()
        self.button.rect.width = 50
        self.button.rect.height = 50
        self.button.color_active = (0, 0, 205)
        self.button.color_inactive = (0, 0, 255)
        self.button.func = self.start_the_story_game

    def draw(self):
        # Update backspace
        if self.del_bool and time.time() > self.del_time + .2:
            self.del_time = time.time()
            self.text = self.text[:-1]

        self.button.draw()
        pygame.draw.rect(screen, (0, 0, 0), self.rect)

        pygame.draw.rect(screen, (0, 150, 255), rect_border(self.rect, -4))
        if self.text == '':
            self.text_object = font_object.render("Wpisz nazwę pliku", False, (0, 20, 20))
        else:
            self.text_object = font_object.render(self.text, False, (0, 0, 0))
        screen.blit(self.text_object, self.text_object.get_rect(
            center=((self.rect.x + self.rect.width / 2), self.rect.y + (self.rect.height / 2))))

    def start_the_story_game(self, _):
        global story
        try:
            story = __import__(self.text).story
        except Exception as e:
            print("no story found or an error with a story")
            print(e)
            return
        global run
        run = True
        return

    def update(self, event: pygame.event):
        self.button.update(event)
        if event.type == KEYUP:
            if event.key == K_BACKSPACE:
                self.del_bool = False
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.del_bool = True
                self.text = self.text[:-1]
                self.del_time = time.time()
            elif event.key == K_RETURN:
                return self.start_the_story_game()
            else:
                self.text += event.unicode


text_input = InputText(100, 100)

for i in range(5):
    Button(50, 250 + (i * 60), func=button_function)

while True:

    # load story loop
    while not run:
        screen.fill((0, 255, 0))
        text_input.draw()
        for event in pygame.event.get():
            text_input.update(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()

    # story loop
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
