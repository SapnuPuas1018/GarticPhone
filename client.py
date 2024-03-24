import pygame
import sys
import os

# Constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
REFRESH_RATE = 16500

PRESS_START_IMAGE_PATH = r'C:\Users\nati2\PycharmProjects\GarthicPhone\press_start.png'


def draw_circle_at_cursor(screen, radius, color):
    # Get the current cursor position
    pos = pygame.mouse.get_pos()

    # Draw the circle at the cursor position
    pygame.draw.circle(screen, color, pos, radius)


def draw_screen(screen, clock):
    pygame.display.set_caption("Draw Circle at Cursor")
    screen.fill('black')
    # circle properties
    circle_radius = 3
    circle_color = (0, 255, 255)  # Green

    draw = False

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Draw the circle at the cursor
                draw = True
            if event.type == pygame.MOUSEBUTTONUP:
                draw = False

        if draw:
            draw_circle_at_cursor(screen, circle_radius, circle_color)

        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def main_menu(screen, clock):
    pygame.display.set_caption("Garthicc Phone")

    # basic font for user typed
    base_font = pygame.font.Font(None, 32)
    user_text = ''

    # create rectangle
    input_rect = pygame.Rect(200, 200, 140, 32)

    # color_active stores color(lightskyblue3) which
    # gets active when input box is clicked by user
    color_active = pygame.Color('lightskyblue3')

    # color_passive store color(chartreuse4) which is
    # color of input box.
    color_passive = pygame.Color('chartreuse4')
    color = color_passive

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    active = False
                    # if user_text is not '':
                    #     socket.send(user_text)
                    #     active = False
                    # else
                    #     print('write something')
                if event.key == pygame.K_BACKSPACE:
                    # get text input from 0 to -1 i.e. end.
                    user_text = user_text[:-1]

                    # Unicode standard is used for string
                # formation
                else:
                    user_text += event.unicode

        screen.fill((255, 255, 255))
        if active:
            color = color_active
        else:
            color = color_passive

        # draw rectangle and argument passed which should
        # be on screen
        pygame.draw.rect(screen, color, input_rect)

        text_surface = base_font.render(user_text, True, (255, 255, 255))
        # render at position stated in arguments
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # set width of textfield so that text cannot get
        # outside of user's text input
        input_rect.w = max(100, text_surface.get_width() + 10)

        # display.flip() will update only a portion of the
        # screen to updated, not full area
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def start_screen(screen, clock):
    pygame.display.set_caption("Garthicc Phone")
    img = pygame.image.load(PRESS_START_IMAGE_PATH)
    screen.blit(img, (0, 0))

    input_rect = pygame.Rect(200, 200, 300, 64)

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if input_rect.collidepoint(event.pos):
                    active = False

        # Update the display
        pygame.display.flip()
        clock.tick(REFRESH_RATE)


def get_screen():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    size = (screen_width, screen_height)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    return screen


def main():
    pygame.init()
    # it will display on screen
    # size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = get_screen()
    clock = pygame.time.Clock()

    start_screen(screen, clock)

    main_menu(screen, clock)

    draw_screen(screen, clock)

    pygame.quit()


if __name__ == "__main__":
    main()
