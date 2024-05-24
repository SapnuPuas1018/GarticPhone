import pygame
import os
import socket
import logging

from AnimatedButton import AnimatedButton
from InputBox import InputBox


# Constants
FONT = pygame.font.SysFont('arialblack', 32)
# screen
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
REFRESH_RATE = 165
# buttons

# server
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5555

PRESS_START_IMAGE_PATH = r'C:\Users\nati2\PycharmProjects\GarthicPhone\press_start.png'

logging.basicConfig(filename='my_log_client.log', level=logging.DEBUG)


def draw_text(text, font, text_color, x, y, screen):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_circle_at_cursor(screen, radius, color):
    # Get the current cursor position
    pos = pygame.mouse.get_pos()
    # Draw the circle at the cursor position
    pygame.draw.circle(screen, color, pos, radius)


def brush_sizes(screen):
    xl_brush = pygame.draw.rect(screen, 'black', [10, 10, 50, 50])
    pygame.draw.circle(screen, 'white', (35, 35), 20)

    l_brush = pygame.draw.rect(screen, 'black', [70, 10, 50, 50])
    pygame.draw.circle(screen, 'white', (95, 35), 15)

    m_brush = pygame.draw.rect(screen, 'black', [130, 10, 50, 50])
    pygame.draw.circle(screen, 'white', (155, 35), 10)

    s_brush = pygame.draw.rect(screen, 'black', [190, 10, 50, 50])
    pygame.draw.circle(screen, 'white', (215, 35), 5)

    brush_list = [xl_brush, l_brush, m_brush, s_brush]
    return brush_list


def color_palette(screen):
    blue = pygame.draw.rect(screen, (0, 0, 255), [720 - 35, 10, 25, 25])
    red = pygame.draw.rect(screen, (255, 0, 0), [720 - 35, 35, 25, 25])
    green = pygame.draw.rect(screen, (0, 255, 0), [720 - 60, 10, 25, 25])
    yellow = pygame.draw.rect(screen, (255, 255, 0), [720 - 60, 35, 25, 25])
    teal = pygame.draw.rect(screen, (0, 255, 255), [720 - 85, 10, 25, 25])
    purple = pygame.draw.rect(screen, (255, 0, 255), [720 - 85, 35, 25, 25])
    white = pygame.draw.rect(screen, (255, 255, 255), [720 - 110, 10, 25, 25])
    black = pygame.draw.rect(screen, (0, 0, 0), [720 - 110, 35, 25, 25])

    color_list = [blue, red, green, yellow, teal, purple, white, black]
    rgb_list = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255),
                (0, 0, 0)]
    return color_list, rgb_list


def draw_screen(screen, clock):
    pygame.display.set_caption("Draw Circle at Cursor")
    screen.fill((52, 78, 91))
    canvas = pygame.draw.rect(screen, 'white', [192, 90, 896, 540])

    active_size = 15
    active_color = 'Black'

    brush_list = brush_sizes(screen)
    color_list, rgb_list = color_palette(screen)

    DONE_BUTTON = AnimatedButton('Done', 150, 40, (938, 658), 8)

    CLEAR_BUTTON = AnimatedButton('Clear', 150, 40, (192, 658), 8)

    buttons_list = [DONE_BUTTON, CLEAR_BUTTON]

    draw = False
    done = False
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # brush size
                for i in range(len(brush_list)):
                    if brush_list[i].collidepoint(pygame.mouse.get_pos()):
                        active_size = 18 - (i * 5)
                # brush's color
                for i in range(len(color_list)):
                    if color_list[i].collidepoint(pygame.mouse.get_pos()):
                        active_color = rgb_list[i]
                # draw
                draw = True
            if event.type == pygame.MOUSEBUTTONUP:
                draw = False

            if event.type == pygame.MOUSEBUTTONUP:
                draw = False
                if CLEAR_BUTTON.pressed:
                    pygame.draw.rect(screen, 'white', [192, 90, 896, 540])
                if DONE_BUTTON.pressed:
                    done = not done

        pygame.draw.rect(screen, active_color, [16, 566, 160, 64], 0, 7)

        for button in buttons_list:
            button.draw(screen)

        if not done and draw:
            clip = pygame.Rect((192, 90, 896, 540))
            screen.set_clip(clip)
            draw_circle_at_cursor(screen, active_size, active_color)
            screen.set_clip(None)

        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def main_menu(screen, clock, my_socket):
    pygame.display.set_caption("Garthicc Phone")
    # READY_BUTTON = Button(image=None, pos=(100, 100),
    #                       text_input="READY", font=FONT, base_color="White", hovering_color="Black")
    READY_BUTTON = AnimatedButton('Ready', 200, 40, (100, 100), 8)
    button_list = [READY_BUTTON]
    my_socket.setblocking(False)
    is_ready = False
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.MOUSEBUTTONUP:
                if READY_BUTTON.pressed:
                    is_ready = not is_ready
                    if is_ready:
                        READY_BUTTON.set_text('Unready')
                    else:
                        READY_BUTTON.set_text('Ready')
                    my_socket.send(str(is_ready).encode())
                    print(is_ready)

        try:
            data = my_socket.recv(1024).decode()
            if data == 'game started':
                print('check')
                active = False
        except BlockingIOError:
            pass

        screen.fill((52, 78, 91))
        for button in button_list:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def join_screen(screen, clock, my_socket):
    pygame.display.set_caption("join screen")

    screen.fill((52, 78, 91))

    JOIN_BUTTON = AnimatedButton('JOIN', 200, 40, (100, 100), 8)
    buttons_list = [JOIN_BUTTON]

    user_name = ''
    input_box = InputBox(560, 344, 140, 32)
    input_boxes = [input_box]

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            for box in input_boxes:
                input_box.handle_event(event)
                user_name = box.text
            if event.type == pygame.MOUSEBUTTONUP:
                if JOIN_BUTTON.pressed:
                    if user_name != '' and user_name is not None:
                        try:
                            print(user_name)
                            my_socket.connect(('127.0.0.1', SERVER_PORT))
                            logging.debug('connected')
                            active = False
                            my_socket.send(user_name.encode())
                        except socket.error as err:
                            logging.error('received socket error on client socket' + str(err))
                            print('received socket error on client socket' + str(err))
                            active = True
        screen.fill((52, 78, 91))
        draw_text('Enter your name:', FONT, (255, 255, 255), 160, 250, screen)
        for button in buttons_list:
            button.draw(screen)

        for box in input_boxes:
            box.update()
        for box in input_boxes:
            box.draw(screen)
        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)
    return True


def start_screen(screen, clock):
    pygame.display.set_caption("Garthicc Phone")
    # img = pygame.image.load(PRESS_START_IMAGE_PATH)
    # screen.blit(img, (0, 0))

    screen.fill((52, 78, 91))

    draw_text('press any key to start', FONT, (255, 255, 255), 160, 250, screen)
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                active = False
            if event.type == pygame.QUIT:
                return False

        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)
    return True

def set_screen():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    size = (screen_width - 10, screen_height - 50)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    return screen


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


def main():
    pygame.init()
    pygame.font.init()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()

        if start_screen(screen, clock):
            if join_screen(screen, clock, my_socket):
                main_menu(screen, clock, my_socket)
                draw_screen(screen, clock)
    except socket.error as err:
        logging.error('received socket error on client socket' + str(err))
        print('received socket error on client socket' + str(err))
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
