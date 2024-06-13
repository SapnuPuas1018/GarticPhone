import logging
import socket
import threading
import time
from threading import Thread
from player import Player
from protocol import *
import json

logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)

IP = '127.0.0.1'
PORT = 5557
QUEUE_LEN = 20
MAX_PACKET = 1024
LOCK_COUNT = threading.Lock()

player_dict = []

ready_count = 0
game_started = False

sentences_count = 0
send_sentence_count = 0

drawings_count = 0
send_drawings_count = 0

switches = 0


def send_to_everyone(player_dict, data):
    for sock in player_dict:
        send(sock.socket, data)


def wait_for_ready(client_socket, player_dict):
    global ready_count
    while len(player_dict) != ready_count or len(player_dict) < 3:

        is_ready = recv(client_socket)
        if is_ready == 'all players are ready':
            break

        if is_ready == 'True':
            ready_count += 1
        else:
            ready_count -= 1
        print(ready_count)
        print('ready players count:' + str(ready_count))
        print(f'i sent: {ready_count}/{len(player_dict)}')
        send_to_everyone(player_dict, f'{ready_count}/{len(player_dict)}')


def circular_switch(dict):
    global switches
    switches += 1

    if not dict:  # If the dictionary is empty, do nothing
        return

    if switches % len(dict) != 0:
        return dict

    print('circular switch')
    # Get the list of keys and values
    keys = list(dict.keys())
    values = list(dict.values())

    # Rotate the values by one position to the right
    rotated_values = [values[-1]] + values[:-1]

    # Reassign the rotated values to the corresponding keys
    for key, new_value in zip(keys, rotated_values):
        dict[key] = new_value

    return dict


def receive_drawing(client_socket, player_dict, this_player):
    print('waiting to receive a drawing from player - ' + str(this_player))
    global drawings_count
    drawing = recv(client_socket)
    if drawing != '' and drawing is not None:
        print('found a drawing from player: ' + str(this_player))
        print(drawing)
        player_dict[this_player] = drawing
        print(player_dict)

    drawings_count += 1
    print('ready drawings: ' + str(drawings_count))


def receive_sentence(client_socket, player_dict, this_player):
    print('waiting to receive a sentence from player - ' + str(this_player))
    global sentences_count
    while True:
        sentence = recv(client_socket)
        if sentence != '' and sentence is not None and sentence != 'all players are ready':
            print('found a sentence from player: ' + sentence + ', from: ' + str(this_player))
            player_dict[this_player] = sentence
            break

    sentences_count += 1
    print('ready sentences: ' + str(sentences_count))


def send_sentence(client_socket, player_dict, this_player):
    global send_sentence_count
    print('waiting to player request for sentence - ' + str(this_player))
    while True:
        request = recv(client_socket)
        if request == 'give sentence':
            print("sending the sentence: " + str(player_dict[this_player]) + " to player: " + str(this_player))
            send(client_socket, player_dict[this_player])
            break

    send_sentence_count += 1
    print('ready sentences: ' + str(sentences_count))


def send_drawings(client_socket, player_dict_drawing, this_player):
    global send_drawings_count
    print('waiting to player request for drawing - ' + str(this_player))
    while True:
        request = recv(client_socket)
        if request == 'give drawing':
            print("sending the drawing to player: " + str(this_player))
            send(client_socket, player_dict_drawing[this_player])
            break

    send_drawings_count += 1
    print('ready sentences: ' + str(drawings_count))


def handle_connection(client_socket, player_dict, this_player):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    global game_started
    try:
        # ----------------------------------------------------------------------players ready
        global switches
        send(client_socket, f'{ready_count}/{len(player_dict)}')

        wait_for_ready(client_socket, player_dict)
        print('game started')
        game_started = True
        # ----------------------------------------------------------------------first sentence
        receive_sentence(client_socket, player_dict, this_player)
        # checks if everyone has sent their sentence

        # while sentences_count != len(player_dict):
        #     pass
        while sentences_count != 0 and sentences_count % len(player_dict) != 0:
            pass
        print('received all sentences')
        send(client_socket, 'start drawing')
        i = 0
        while i < len(player_dict) - 1:
            # ----------------------------------------------------------------------drawing

            player_dict = circular_switch(player_dict)
            print(str(player_dict))

            global send_sentence_count
            send_sentence(client_socket, player_dict, this_player)
            # while len(player_dict) != send_sentence_count:
            #     pass
            while send_sentence_count != 0 and send_sentence_count % len(player_dict) != 0:
                pass

            print('waiting for receiving drawings')

            player_dict_drawing = player_dict
            receive_drawing(client_socket, player_dict_drawing, this_player)

            while drawings_count != 0 and drawings_count % len(player_dict_drawing):
                pass

            print('received all drawings')
            i += 1
            if i == len(player_dict) - 1:
                break
            # ---------------------------------------------------------------------guessing / show image
            send(client_socket, 'start guessing')

            player_dict_drawing = circular_switch(player_dict_drawing)
            print(str(player_dict))

            global send_drawings_count
            send_drawings(client_socket, player_dict_drawing, this_player)

            # while len(player_dict_drawing) != send_drawings_count:
            #     pass
            while send_drawings_count != 0 and send_drawings_count % len(player_dict_drawing) != 0:
                pass
            print('waiting for receiving sentences')

            player_dict = player_dict_drawing
            receive_sentence(client_socket, player_dict, this_player)

            # while len(player_dict) != sentences_count:
            #     pass
            while sentences_count != 0 and sentences_count % len(player_dict) != 0:
                pass

            print('received all sentences')
            i += 1
            send(client_socket, 'start drawing')

        print('done')

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        print('closing client socket')
        client_socket.close()
        print('client socket closed')

def main():
    """
    Initializes and manages the socket server.
    :return: None
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_LEN)
        logging.debug('waiting for connection...')
        print("Listening for connections on port %d" % PORT)

        player_dict = {}
        while True:
            client_socket, client_address = server_socket.accept()
            print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))

            name = recv(client_socket)
            this_player = Player(name, client_socket, client_address)
            player_dict[this_player] = ''

            thread = Thread(target=handle_connection,
                            args=(client_socket, player_dict, this_player))
            thread.start()

    except socket.error as err:
        logging.error('received socket error on server socket' + str(err))
        print('received socket error on client socket' + str(err))

    finally:
        print('closing server socket')
        server_socket.close()
        print('client socket closed')


if __name__ == '__main__':
    main()
