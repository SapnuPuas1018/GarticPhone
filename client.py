import base64
import io

import pygame
import os
import socket
import logging
import time
import pyscreeze
from io import BytesIO
import base64
from PIL import Image
from protocol import *

from AnimatedButton import AnimatedButton
from InputBox import InputBox


# Constants
FONT = pygame.font.SysFont('arialblack', 32)
# screen
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
REFRESH_RATE = 165
FILE_PATH_FOR_SCREENSHOTS = 'screenshot.jpg'
# buttons

# server
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5557

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
    x = 136
    y = 500
    z = 475
    blue = pygame.draw.rect(screen, (0, 0, 255), [x - 35, z, 25, 25])
    red = pygame.draw.rect(screen, (255, 0, 0), [x - 35, y, 25, 25])
    green = pygame.draw.rect(screen, (0, 255, 0), [x - 60, z, 25, 25])
    yellow = pygame.draw.rect(screen, (255, 255, 0), [x - 60, y, 25, 25])
    teal = pygame.draw.rect(screen, (0, 255, 255), [x - 85, z, 25, 25])
    purple = pygame.draw.rect(screen, (255, 0, 255), [x - 85, y, 25, 25])
    white = pygame.draw.rect(screen, (255, 255, 255), [x - 110, z, 25, 25])
    black = pygame.draw.rect(screen, (0, 0, 0), [x - 110, y, 25, 25])

    color_list = [blue, red, green, yellow, teal, purple, white, black]
    rgb_list = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255),
                (0, 0, 0)]
    return color_list, rgb_list


def string_to_image(base64_string):
    image_data = base64.b64decode(base64_string)

    # Create a PIL image from the binary data
    image = Image.open(io.BytesIO(image_data))

    # Convert Pillow image to Pygame surface
    pygame_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    return pygame_image


def show_image(screen, clock, my_socket):
    print("requesting a drawing from server...")
    my_socket.setblocking(True)
    send(my_socket, 'give drawing')
    print('asking for a drawing')

    drawing = recv(my_socket)
    print('i received a drawing')

    SEND_BUTTON = AnimatedButton('Send', 150, 40, (938, 658), 8)
    screen.fill((52, 78, 91))

    my_socket.setblocking(False)

    sentence = ''
    input_box = InputBox(560, 680, 140, 32)
    input_boxes = [input_box]

    sent = False
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if SEND_BUTTON.pressed:
                    if sentence != '' and sentence is not None:
                        send(my_socket, sentence)
                        print('I sent: ' + sentence)
                        sent = True
                        SEND_BUTTON.pressed = False
            for box in input_boxes:
                input_box.handle_event(event)
                sentence = box.text
            screen.fill((52, 78, 91))
            for box in input_boxes:
                box.update()
                box.draw(screen)
            if not sent:
                SEND_BUTTON.draw(screen)
            # Update the display
            screen.blit(string_to_image(drawing), (192, 90))
            # try:
            #     data = recv(my_socket)
            #
            # except BlockingIOError:
            #     pass

            # Update the display
            pygame.display.flip()
            clock.tick(REFRESH_RATE)


def draw_screen(screen, clock, my_socket):
    print("requesting a sentence from server...")
    my_socket.setblocking(True)
    send(my_socket, 'give sentence')

    sentence = recv(my_socket)
    print(f"my sentence is: {sentence}")

    pygame.display.set_caption("Draw Circle at Cursor")
    screen.fill((52, 78, 91))
    canvas = [192, 90, 896, 540]

    pygame.draw.rect(screen, 'white', canvas)

    active_size = 15
    active_color = 'Black'

    brush_list = brush_sizes(screen)
    color_list, rgb_list = color_palette(screen)

    DONE_BUTTON = AnimatedButton('Done', 150, 40, (938, 658), 8)
    CLEAR_BUTTON = AnimatedButton('Clear', 150, 40, (192, 658), 8)

    buttons_list = [DONE_BUTTON, CLEAR_BUTTON]

    my_socket.setblocking(False)

    left, top, width, height = (192, 90, 896, 540)

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

                if CLEAR_BUTTON.pressed:
                    if not done:
                        pygame.draw.rect(screen, 'white', canvas)
                if DONE_BUTTON.pressed:
                    done = not done
                    if done:
                        DONE_BUTTON.set_text('Edit')
                        sub = screen.subsurface(canvas)
                        pygame.image.save(sub, FILE_PATH_FOR_SCREENSHOTS)
                        with open(FILE_PATH_FOR_SCREENSHOTS, 'rb') as image_file:
                            drawing = base64.b64encode(image_file.read()).decode('utf-8')

                            # Ensure socket is non-blocking before sending
                            my_socket.setblocking(False)
                            try:
                                print('im sending a drawing')
                                send(my_socket, drawing)
                                print('I sent a drawing')
                                print(drawing)
                            except socket.error as err:
                                logging.error('Error sending drawing: ' + str(err))
                                print('Error sending drawing: ' + str(err))

                    else:
                        DONE_BUTTON.set_text('Done')

        pygame.draw.rect(screen, active_color, [16, 566, 160, 64], 0, 7)

        for button in buttons_list:
            button.draw(screen)

        if not done and draw:
            clip = pygame.Rect((192, 90, 896, 540))
            screen.set_clip(clip)
            draw_circle_at_cursor(screen, active_size, active_color)
            screen.set_clip(None)

        if sentence is not None:
            draw_text(sentence, FONT, 'white', 600, 0, screen)

        try:
            data = recv(my_socket)
            if data == 'start guessing':
                print("Server detected all drawings, moving on...")
                active = False
        except BlockingIOError:
            pass
        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def first_sentence(screen, clock, my_socket):
    SEND_BUTTON = AnimatedButton('Send', 150, 40, (938, 658), 8)
    screen.fill((52, 78, 91))

    my_socket.setblocking(False)

    sentence = ''
    input_box = InputBox(560, 344, 140, 32)
    input_boxes = [input_box]

    sent = False
    active = True
    recv_buffer = ''
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                if SEND_BUTTON.pressed:
                    if sentence != '' and sentence is not None:
                        send(my_socket, sentence)
                        print('I sent: ' + sentence)
                        sent = True
                        SEND_BUTTON.pressed = False
            for box in input_boxes:
                input_box.handle_event(event)
                sentence = box.text

        screen.fill((52, 78, 91))
        for box in input_boxes:
            box.update()
        for box in input_boxes:
            box.draw(screen)

        if not sent:
            SEND_BUTTON.draw(screen)
        # Update the display
        pygame.display.flip()
        try:
            data = recv(my_socket)
            if data == 'start drawing':
                print("Server detected the sentences moving to game...")
                active = False
        except BlockingIOError:
            pass

        try:
            data = recv(my_socket)
            if data == 'start drawing':
                print("Server detected the sentences moving to game...")
                active = False
        except BlockingIOError:
            pass

        clock.tick(REFRESH_RATE)
    return True


def lobby(screen, clock, my_socket):
    pygame.display.set_caption("Gartic Phone")
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
                    send(my_socket, str(is_ready))
                    print(is_ready)

        try:
            data = recv(my_socket)
            print('i received: ' + data)
            draw_text(data, FONT, (255, 255, 255), 160, 250, screen)    # Doesn't work for some reason
            players_ready, total_players = data.split('/')
            if 2 <= int(players_ready) == int(total_players):
                print('all players are ready, moving to the sentences screen')
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
                quit()
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
                            send(my_socket, user_name)
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
    pygame.display.set_caption("Gartic Phone")
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
                quit()

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
                lobby(screen, clock, my_socket)
                first_sentence(screen, clock, my_socket)
                draw_screen(screen, clock, my_socket)
                print('hi im here')
                show_image(screen, clock, my_socket)
    except socket.error as err:
        logging.error('received socket error on client socket' + str(err))
        print('received socket error on client socket' + str(err))
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
