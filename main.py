import time
import sys
import random
import pygame
from pygame.locals import *

pygame.init()
selected_block = None
rel_mouse_poz = pygame.mouse.get_rel()
blocks_list = []
settings_things = []
running = True

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
        max_width = screen.get_width() - 20
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
            index = 0
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
        self.parent = None
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
        self.width = 350
        self.rect = pygame.Rect(x, y, self.width, 50)
        self.text = ''
        self.text_object = font_object.render(self.text, False, (0, 0, 0))
        self.del_bool = False
        self.del_time = time.time()
        self.button = Button(x - 48, y)
        self.button.parent = self
        self.button.destroy()
        self.button.rect.width = 50
        self.button.rect.height = 50
        self.button.color_active = (0, 255, 0)
        self.button.color_inactive = (0, 200, 0)
        self.error = ''
        self.error_time = time.time()
        self.error_color = (255, 0, 0)
        self.button.func = self.run_function
        self.default_text = "Enter file name"
        self.selected = False

    def draw(self):
        # Update backspace
        if self.del_bool and time.time() > self.del_time + .2:
            self.del_time = time.time()
            self.text = self.text[:-1]
        # Update other stuff
        self.rect.width = max(self.width, self.text_object.get_width())

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
            if self.selected:
                self.text_object = font_object.render(
                    '|' if self.selected and round(time.time() * 1.8) % 2 == 0 else ' ', False, (0, 20, 20))
            else:
                self.text_object = font_object.render(self.default_text, False, (0, 20, 20))
        else:
            self.text_object = font_object.render(
                self.text + ('|' if self.selected and round(time.time() * 1.8) % 2 == 0 else ' '), False, (0, 0, 0))
        screen.blit(self.text_object, self.text_object.get_rect(
            center=((self.rect.x + self.rect.width / 2), self.rect.y + (self.rect.height / 2))))

    def run_function(self, _):
        if self.text == ":ADMIN":
            global editor_button
            editor_button.visible = True
            self.text = ''
            self.error = "Good luck admin!"
            self.error_time = time.time() + 2
            self.selected = False
            return
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
        self.selected = False
        return self.text

    def update(self, event: pygame.event):
        self.button.update(event)
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.selected = True
            else:
                self.selected = False
        if event.type == KEYUP:
            if event.key == K_BACKSPACE:
                self.del_bool = False
        if event.type == KEYDOWN and self.selected:
            if event.key == K_BACKSPACE:
                self.del_bool = True
                self.text = self.text[:-1]
                self.del_time = time.time()
            elif event.key == K_RETURN:
                return self.run_function(self.button)
            else:
                self.text += event.unicode


class Block:
    def __init__(self, x, y):
        blocks_list.append(self)
        self.rect = pygame.Rect(x, y, 700, 70)
        self.draw_rect = self.rect.copy()
        self.color = (50, 50, 50)
        self.selected = False
        self.text_inputs = []
        self.main_text_input = InputText(x, y)
        self.text_inputs.append(self.main_text_input)
        self.main_text_input.default_text = 'Main text here'
        self.main_text_input.rect.width = max(self.main_text_input.text_object.get_rect().width, 100)
        self.parent = None
        self.child = None
        for x in range(6):
            self.text_inputs.append(InputText(x, y))
            self.text_inputs[-1].default_text = ''
            self.text_inputs[-1].width = 50
            self.text_inputs[-1].button.visible = False

    def update_child_position(self):
        if self.child is not None:
            self.child.draw_rect.midtop = self.draw_rect.midbottom
            self.child.rect.midtop = self.draw_rect.midbottom
            self.child.update_child_position()

    def update_values(self):
        # update values
        current_width = 60
        self.main_text_input.rect.midleft = self.draw_rect.midleft
        self.main_text_input.rect.x += 60
        self.main_text_input.width = 300
        self.main_text_input.button.rect.midright = self.main_text_input.rect.midleft
        self.main_text_input.button.rect.x += 2
        for index, text_input in enumerate(self.text_inputs):
            current_width += text_input.rect.width
            if index != 0:
                text_input.rect.midleft = self.text_inputs[index - 1].rect.midright
                text_input.rect.x -= 4
        self.rect.width = current_width
        self.draw_rect = self.rect.copy()

        self.update_child_position()
        if self.parent is not None:
            self.rect.midtop = self.parent.rect.midbottom
            if self.parent.rect.collidepoint(pygame.mouse.get_pos()):
                self.draw_rect.midtop = self.parent.rect.midbottom
            elif self.selected:
                self.parent.child = None
                self.parent = None

    def draw(self):
        self.update_values()
        # draw
        pygame.draw.rect(screen, self.color, self.draw_rect)
        for input_box in reversed(self.text_inputs):
            input_box.draw()

    def update(self, event):
        global selected_block, rel_mouse_poz
        for input_box in reversed(self.text_inputs):
            input_box.update(event)
        if event.type == MOUSEBUTTONUP:
            self.selected = False
            if selected_block == self:
                selected_block = None
            self.rect = self.draw_rect.copy()
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.selected = True
                selected_block = self
        if event.type == MOUSEMOTION:
            if self.selected:
                rel_mouse_poz = pygame.mouse.get_rel()

                self.rect.x += rel_mouse_poz[0]
                self.rect.y += rel_mouse_poz[1]

            elif selected_block is not None:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    if self.child:
                        self.child.parent = None
                    if self.parent:
                        self.parent.child = None
                    # if selected_block.parent:
                    self.child = selected_block
                    selected_block.parent = self


text_input = InputText(100, 100)
bg_color = (70, 70, 70)
clock = pygame.time.Clock()

# Define the editor button (it opens a story editor)
editor_button = Button(50, 250)
editor_button.destroy()  # deletes it from the update list :)
editor_button.set_text("Open Story Editor")
# Define the font selector
font_selector = InputText(100, 100)
font_selector.default_text = 'Font'
settings_things.append(font_selector)


def select_font(button: Button):
    global font_object
    if button.parent is None:
        return
    input_box: InputText = button.parent
    font_object = pygame.font.SysFont(input_box.text, size=55)


font_selector.run_function = select_font
font_selector.button.func = select_font
# Define the bg_color selector
bg_color_selector = InputText(100, 170)
bg_color_selector.width = 500
bg_color_selector.default_text = 'Background color (RGB)'
settings_things.append(bg_color_selector)


def exit_settings(button):
    global running
    button.func = settings_loop
    button.set_text('Settings')
    running = False


def select_bg_color(button):
    global bg_color
    if button.parent is None:
        return
    input_box: InputText = button.parent
    bg_color = tuple(int(input_box.text.split(',')[index]) for index in range(3))


bg_color_selector.run_function = select_bg_color

bg_color_selector.button.func = select_bg_color

exit_editor_button = Button(5, 5)
exit_editor_button.destroy()
exit_editor_button.rect.width = 50
exit_editor_button.rect.height = 50
exit_editor_button.set_text('X')


def exit_small_menus(_):
    global running
    running = False


exit_editor_button.func = exit_small_menus

for i in range(10):
    Block(150, 150 + (80 * i))

# Hide the unsupported editor_button
editor_button.visible = False
def editor_loop(button):
    global rel_mouse_poz, running
    running = True
    while running:
        screen.fill(bg_color)
        for block in blocks_list:
            block.draw()
        exit_editor_button.draw()
        for event in pygame.event.get():
            for block in blocks_list:
                block.update(event)
            exit_editor_button.update(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        rel_mouse_poz = pygame.mouse.get_rel()
        pygame.display.flip()


editor_button.func = editor_loop

settings_button = Button(2, 2)
settings_button.destroy()  # removes it from the list
settings_things.append(settings_button)
settings_button.rect.width = 170
settings_button.set_text('Settings')


def settings_loop(button):
    global running
    running = True
    button.set_text('Back')

    button.func = exit_settings
    while running:
        screen.fill(bg_color)
        for thing in settings_things:
            thing.draw()
        for event in pygame.event.get():
            for thing in settings_things:
                thing.update(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()


settings_button.func = settings_loop

for i in range(5):
    Button(50, 250 + (i * 60), func=button_function)

while True:

    # load story loop
    while not run:
        dt = clock.tick(60)
        screen.fill(bg_color)
        text_input.draw()
        editor_button.draw()
        settings_button.draw()
        for event in pygame.event.get():
            text_input.update(event)
            editor_button.update(event)
            settings_button.update(event)
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
        for rect in text_object_thingy:
            temp_rect.width = max(temp_rect.width, rect.get_width())
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
            elif event.type == pygame.VIDEORESIZE:

                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        pygame.display.update()

    text_input.text = ''
