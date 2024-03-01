import time
import sys
import random
import pygame
from pygame.locals import *

selected_block = None

pygame.init()

pygame.display.set_caption("Fabular Game Creator")
screen = pygame.display.set_mode((1000, 1000), RESIZABLE)
button_list = []
story = []

run = False
font_object = pygame.font.SysFont('your font', size=55)

index = 0
text_at_the_top = ''

def render_text(text, color=(0, 0, 0), font=font_object, max_width=None):
    if max_width is None:
        max_width = screen.get_width()
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)

    rendered_lines = []
    y_offset = 0
    for line in lines:
        text_surface = font.render(line, True, color)
        rendered_lines.append(text_surface)
        y_offset += font.get_linesize()

    return rendered_lines

def rect_border(rect, border_size):
    return pygame.Rect(rect.x - border_size, rect.y - border_size, rect.width + (2 * border_size),
                       rect.height + (2 * border_size))


def add_colors(*args):
    x, y, z = 0, 0, 0
    for color in args:
        x += color[0]
        y += color[1]
        z += color[2]
    return min(x, 255), min(y, 255), min(z, 255)


def rect_gradient(in_color, out_color, rect, steps, width=1):
    rect = rect_border(rect, steps * width)
    x = out_color[0]
    y = out_color[1]
    z = out_color[2]
    dx = (in_color[0] - x) // steps
    dy = (in_color[1] - y) // steps
    dz = (in_color[2] - z) // steps
    for step in range(steps + 1):
        pygame.draw.rect(screen, (x, y, z), rect_border(rect, -step * width))
        x += dx
        y += dy
        z += dz


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
        self.font = font_object.render(self.text, False, (0, 0, 0))
        self.color_inactive = (0, 150, 200)
        self.color_active = (0, 160, 255)
        self.held = False
        self.visible = True
        self.extra_border = 0

    def draw(self):
        if not self.visible:
            return
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.extra_border = 2
        else:
            self.extra_border = 0
        pygame.draw.rect(screen, (0, 0, 0), rect_border(self.rect, self.extra_border))
        if self.held:
            pygame.draw.rect(screen, self.color_active, rect_border(self.rect, self.extra_border - 4))
        else:
            pygame.draw.rect(screen, self.color_inactive, rect_border(self.rect, self.extra_border - 4))

        screen.blit(self.font, self.font.get_rect(
            center=((self.rect.x + self.rect.width / 2), self.rect.y + (self.rect.height / 2))))

    def set_text(self, text):
        self.text = text
        self.font = font_object.render(text, False, (0, 0, 0))

    def update(self, event):
        if not self.visible:
            return
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.held = True
        elif event.type == MOUSEBUTTONUP:
            self.held = False
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return self.func(self)

    def destroy(self):
        button_list.remove(self)
        del self


class InputText:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 350, 50)
        self.text = ''
        self.text_object = font_object.render(self.text, False, (0, 0, 0))
        self.del_bool = False
        self.del_time = time.time()
        self.button = Button(x - 48, y)
        self.button.destroy()
        self.button.rect.width = 50
        self.button.rect.height = 50
        self.button.color_active = (0, 255, 0)
        self.button.color_inactive = (0, 200, 0)
        self.error = ''
        self.error_time = time.time()
        self.error_color = (255, 0, 0)
        self.button.func = self.start_the_story_game
        self.default_text = "Enter file name"

    def draw(self):
        # Update backspace
        if self.del_bool and time.time() > self.del_time + .2:
            self.del_time = time.time()
            self.text = self.text[:-1]

        self.button.draw()
        pygame.draw.rect(screen, (0, 0, 0), self.rect)

        pygame.draw.rect(screen, (0, 150, 255), rect_border(self.rect, -4))
        if self.error != '':
            if self.error_time - time.time() > 0:
                self.text_object = font_object.render(self.error, False, (0, 20, 20))
            else:
                self.error = ''
                self.text = ''
        elif self.text == '':
            self.text_object = font_object.render(self.default_text, False, (0, 20, 20))
        else:
            self.text_object = font_object.render(self.text, False, (0, 0, 0))
        screen.blit(self.text_object, self.text_object.get_rect(
            center=((self.rect.x + self.rect.width / 2), self.rect.y + (self.rect.height / 2))))

    def start_the_story_game(self, _=None):
        global story
        try:
            story = __import__(self.text).story
        except Exception as e:
            if type(e) is ValueError:
                return
            if type(e) is ModuleNotFoundError:
                self.error_time = time.time() + 2
                self.error = "Story not found"
                return
            if self.error == '':
                self.error = "File is corrupted :|"
                self.error_time = time.time() + 2
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

class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 400, 70)
        self.color = (50, 50, 50)
        self.selected = False
        self.text_inputs = []
        self.main_text_input = InputText(x, y)
        self.text_inputs.append(self.main_text_input)
        self.main_text_input.default_text = 'Main text here'
        self.main_text_input.rect.width = max(self.main_text_input.text_object.get_rect().width, 100)
    def draw(self):
        # update values
        self.main_text_input.button.rect.center = self.rect.center
        self.main_text_input.button.rect.x -= 150
        self.main_text_input.rect.midleft = self.main_text_input.button.rect.midright
        self.main_text_input.rect.width = max(self.main_text_input.text_object.get_rect().width + 20, 100)
        self.main_text_input.button.rect.x += 2

        # draw
        pygame.draw.rect(screen, self.color, self.rect)
        self.main_text_input.draw()
    def update(self, event):
        self.main_text_input.update(event)
        if event.type == MOUSEBUTTONUP:
            self.selected = False
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.selected = True
        if event.type == MOUSEMOTION:
            if self.selected:
                self.rect.center = pygame.mouse.get_pos()


text_input = InputText(100, 100)
bg_color = (70, 70, 70)
clock = pygame.time.Clock()

editor_button = Button(50, 250)
editor_button.destroy() # deletes it from the update list :)
editor_button.set_text("Open Story Editor")
editor_button.visible = False

def editor_loop(button):
    block = Block(150, 150)
    while True:
        screen.fill(bg_color)
        block.draw()
        for event in pygame.event.get():
            block.update(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()

editor_button.func = editor_loop
for i in range(5):
    Button(50, 250 + (i * 60), func=button_function)

while True:

    # load story loop
    while not run:
        dt = clock.tick(60)
        screen.fill(bg_color)
        text_input.draw()
        editor_button.draw()
        for event in pygame.event.get():
            text_input.update(event)
            editor_button.update(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()

    # story loop
    set_text()
    while run:
        dt = clock.tick(60)
        screen.fill(bg_color)
        text_object_thingy = render_text(text_at_the_top)


        temp_rect = text_object_thingy[0].get_rect()
        temp_rect.height = len(text_object_thingy) * font_object.get_height()
        temp_rect.topleft = (10, 10)
        rect_gradient((120, 120, 120), bg_color, temp_rect, 5, 2)

        for line_number, line in enumerate(text_object_thingy):
            screen.blit(line, (temp_rect.x, temp_rect.y + line_number * font_object.get_height()))


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

    text_input.text = ''
