import io
import pygame
import os
import logging
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


logging.basicConfig(filename='my_log_client.log', level=logging.DEBUG)


def draw_text(text, font, text_color, x, y, screen):
    """
        Draws text on the screen.

        :param text: The text to be drawn.
        :type text: str
        :param font: The font to be used.
        :type font: pygame.font.Font
        :param text_color: The color of the text.
        :type text_color: tuple
        :param x: The x-coordinate for the text.
        :type x: int
        :param y: The y-coordinate for the text.
        :type y: int
        :param screen: The screen on which to draw the text.
        :type screen: pygame.Surface
        :return: None
        :rtype: None
    """
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_circle_at_cursor(screen, radius, color):
    """
        Draws a circle at the current cursor position.

        :param screen: The screen on which to draw the circle.
        :type screen: pygame.Surface
        :param radius: The radius of the circle.
        :type radius: int
        :param color: The color of the circle.
        :type color: tuple
        :return: None
        :rtype: None
    """
    # Get the current cursor position
    pos = pygame.mouse.get_pos()
    # Draw the circle at the cursor position
    pygame.draw.circle(screen, color, pos, radius)


def brush_sizes(screen):
    """
        Draws brush size options on the screen.

        :param screen: The screen on which to draw the brush sizes.
        :type screen: pygame.Surface
        :return: List of rectangles representing brush size options.
        :rtype: list[pygame.Rect]
    """
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
    """
        Draws a color palette on the screen.

        :param screen: The screen on which to draw the color palette.
        :type screen: pygame.Surface
        :return: Tuple containing a list of rectangles for colors and their RGB values.
        :rtype: tuple[list[pygame.Rect], list[tuple]]
    """
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
    """
        Converts a base64 encoded string to a Pygame image.

        :param base64_string: The base64 encoded string.
        :type base64_string: str
        :return: The converted Pygame image.
        :rtype: pygame.Surface
    """
    image_data = base64.b64decode(base64_string)

    # Create a PIL image from the binary data
    image = Image.open(io.BytesIO(image_data))

    # Convert Pillow image to Pygame surface
    pygame_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    return pygame_image


def show_image(screen, clock, my_socket):
    """
       Displays an image received from the server and handles user input for guessing.

       :param screen: The screen on which to display the image.
       :type screen: pygame.Surface
       :param clock: The Pygame clock object.
       :type clock: pygame.time.Clock
       :param my_socket: The socket for communication with the server.
       :type my_socket: socket.socket
       :return: None
       :rtype: None
    """
    print("requesting a drawing from server...")
    logging.debug("requesting a drawing from server...")
    my_socket.setblocking(True)
    send(my_socket, 'give drawing')

    drawing = recv(my_socket)

    send_button = AnimatedButton('Send', 150, 40, (938, 658), 8)
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
                if send_button.pressed:
                    if sentence != '' and sentence is not None and sentence != 'all players are ready':
                        send(my_socket, sentence)
                        sent = True
                        send_button.pressed = False
            for box in input_boxes:
                input_box.handle_event(event)
                sentence = box.text
            screen.fill((52, 78, 91))
            for box in input_boxes:
                box.update()
                box.draw(screen)
            if not sent:
                send_button.draw(screen)
            # Update the display
            screen.blit(string_to_image(drawing), (192, 90))
            try:
                data = recv(my_socket)
                if data == 'start drawing':
                    active = False
            except BlockingIOError:
                pass

            # Update the display
            pygame.display.flip()
            clock.tick(REFRESH_RATE)


def draw_screen(screen, clock, my_socket):
    """
        Displays a drawing screen and handles user input for drawing.

        :param screen: The screen on which to display the drawing interface.
        :type screen: pygame.Surface
        :param clock: The Pygame clock object.
        :type clock: pygame.time.Clock
        :param my_socket: The socket for communication with the server.
        :type my_socket: socket.socket
        :return: None
        :rtype: None
    """
    print("requesting a sentence from server...")
    logging.debug("requesting a sentence from server...")
    my_socket.setblocking(True)
    send(my_socket, 'give sentence')

    sentence = recv(my_socket)
    print(f"my sentence is: {sentence}")
    logging.debug(f"my sentence is: {sentence}")

    pygame.display.set_caption("Draw Circle at Cursor")
    screen.fill((52, 78, 91))
    canvas = [192, 90, 896, 540]

    pygame.draw.rect(screen, 'white', canvas)

    active_size = 15
    active_color = 'Black'

    brush_list = brush_sizes(screen)
    color_list, rgb_list = color_palette(screen)

    done_button = AnimatedButton('Done', 150, 40, (938, 658), 8)
    clear_button = AnimatedButton('Clear', 150, 40, (192, 658), 8)

    buttons_list = [done_button, clear_button]

    my_socket.setblocking(False)

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

                if clear_button.pressed:
                    if not done:
                        pygame.draw.rect(screen, 'white', canvas)
                if done_button.pressed:
                    done = not done
                    if done:
                        done_button.set_text('Edit')
                        sub = screen.subsurface(canvas)
                        pygame.image.save(sub, FILE_PATH_FOR_SCREENSHOTS)
                        with open(FILE_PATH_FOR_SCREENSHOTS, 'rb') as image_file:
                            drawing = base64.b64encode(image_file.read()).decode('utf-8')

                            # Ensure socket is non-blocking before sending
                            my_socket.setblocking(False)
                            try:
                                send(my_socket, drawing)
                                print('I sent a drawing')
                                logging.debug('I sent a drawing')
                                print(drawing)
                            except socket.error as err:
                                logging.error('Error sending drawing: ' + str(err))
                                print('Error sending drawing: ' + str(err))

                    else:
                        done_button.set_text('Done')

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
                logging.debug("Server detected all drawings, moving on...")
                active = False
        except BlockingIOError:
            pass
        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def first_sentence(screen, clock, my_socket):
    """
        Handles the screen where the player inputs the first sentence.

        :param screen: The screen on which to display the input box and send button.
        :type screen: pygame.Surface
        :param clock: The Pygame clock object.
        :type clock: pygame.time.Clock
        :param my_socket: The socket for communication with the server.
        :type my_socket: socket.socket
        :return: True if the sentence was successfully sent, False if the user quit.
        :rtype: bool
    """
    send_button = AnimatedButton('Send', 150, 40, (938, 658), 8)
    screen.fill((52, 78, 91))

    my_socket.setblocking(False)

    sentence = ''
    input_box = InputBox(560, 344, 140, 32)
    input_boxes = [input_box]

    sent = False
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                if send_button.pressed:
                    if sentence != '' and sentence != 'all players are ready' and sentence is not None:
                        send(my_socket, sentence)
                        print('I sent: ' + sentence)
                        sent = True
                        send_button.pressed = False
            for box in input_boxes:
                input_box.handle_event(event)
                sentence = box.text

        screen.fill((52, 78, 91))
        for box in input_boxes:
            box.update()
        for box in input_boxes:
            box.draw(screen)

        if not sent:
            send_button.draw(screen)
        # Update the display
        pygame.display.flip()
        try:
            data = recv(my_socket)
            if data == 'start drawing':
                print("Server detected the sentences moving to game...")
                logging.debug("Server detected the sentences moving to game...")
                active = False
        except BlockingIOError:
            pass

        try:
            data = recv(my_socket)
            if data == 'start drawing':
                print("Server detected the sentences moving to game...")
                logging.debug("Server detected the sentences moving to game...")
                active = False
        except BlockingIOError:
            pass

        clock.tick(REFRESH_RATE)
    return True


def lobby(screen, clock, my_socket):
    """
        Handles the lobby screen where players wait until everyone is ready.

        :param screen: The screen on which to display the lobby.
        :type screen: pygame.Surface
        :param clock: The Pygame clock object.
        :type clock: pygame.time.Clock
        :param my_socket: The socket for communication with the server.
        :type my_socket: socket.socket
        :return: The total number of players.
        :rtype: int
    """
    pygame.display.set_caption("Gartic Phone")
    ready_button = AnimatedButton('Ready', 200, 40, (100, 100), 8)
    button_list = [ready_button]

    data = recv(my_socket)
    players_ready, total_players = data.split('/')

    my_socket.setblocking(False)
    is_ready = False
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

            if event.type == pygame.MOUSEBUTTONUP:
                if ready_button.pressed:
                    is_ready = not is_ready
                    if is_ready:
                        ready_button.set_text('Unready')
                    else:
                        ready_button.set_text('Ready')
                    send(my_socket, str(is_ready))
                    logging.debug('is player ready?' + str(is_ready))

        try:
            data = recv(my_socket)
            print('i received: ' + data)
            # draw_text('data', FONT, (255, 255, 255), 160, 250, screen)
            players_ready, total_players = data.split('/')
            if 3 <= int(players_ready) == int(total_players):
                print('all players are ready, moving to the sentences screen')
                logging.debug('all players are ready, moving to the sentences screen')
                send(my_socket, 'all players are ready')
                active = False
        except BlockingIOError:
            pass

        screen.fill((52, 78, 91))
        draw_text('players ready: ' + players_ready + '/' + total_players, FONT, (255, 255, 255), 160, 360, screen)
        # draw_text('players: ' + players, FONT, (255, 255, 255), 160, 460, screen)
        for button in button_list:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(REFRESH_RATE)
    return int(total_players)


def join_screen(screen, clock, my_socket):
    """
        Handles the join screen where the player enters their name.

        :param screen: The screen on which to display the join interface.
        :type screen: pygame.Surface
        :param clock: The Pygame clock object.
        :type clock: pygame.time.Clock
        :param my_socket: The socket for communication with the server.
        :type my_socket: socket.socket
        :return: True if the player successfully joined, False if the user quit.
        :rtype: bool
    """
    pygame.display.set_caption("join screen")

    screen.fill((52, 78, 91))

    join_button = AnimatedButton('JOIN', 200, 40, (100, 100), 8)
    buttons_list = [join_button]

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
                if join_button.pressed:
                    if user_name != '' and user_name is not None:
                        try:
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
    """
        Displays the start screen and waits for the user to press a key or mouse button.

        :param screen: The screen on which to display the start message.
        :type screen: pygame.Surface
        :param clock: The Pygame clock object.
        :type clock: pygame.time.Clock
        :return: True if the user started the game, False if the user quit.
        :rtype: bool
    """
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


def get_font(size):  # Returns Press-Start-2P in the desired size
    """
        Returns a font object for rendering text.

        :param size: The desired size of the font.
        :type size: int
        :return: The font object.
        :rtype: pygame.font.Font
    """
    return pygame.font.Font("assets/font.ttf", size)


def main():
    """
    main
    """
    pygame.init()
    pygame.font.init()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()

        if start_screen(screen, clock):
            if join_screen(screen, clock, my_socket):
                total_players = lobby(screen, clock, my_socket)

                first_sentence(screen, clock, my_socket)
                i = 0
                while i < total_players - 1:
                    draw_screen(screen, clock, my_socket)
                    i += 1
                    if i == total_players - 1:
                        break
                    show_image(screen, clock, my_socket)
                    i += 1
    except socket.error as err:
        logging.error('received socket error on client socket' + str(err))
        print('received socket error on client socket' + str(err))
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
