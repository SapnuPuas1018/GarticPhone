import logging
import socket
import threading
import time
from threading import Thread
from player import Player
from protocol import *

logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)

IP = '127.0.0.1'
PORT = 5557
QUEUE_LEN = 20
MAX_PACKET = 1024
LOCK_COUNT = threading.Lock()

player_dict = []
ready_count = 0
count = 0
send_sentence_count = 0
drawings_count = 0
switches = 0


def send_to_everyone(player_dict, data):
    for sock in player_dict:
        sock.socket.send(data.encode())


def wait_for_ready(client_socket):
    global ready_count
    is_ready = recv(client_socket)
    with LOCK_COUNT:
        if is_ready == 'True':
            ready_count += 1
        else:
            ready_count -= 1
        print('ready players count:' + str(ready_count))


def circular_switch(dict):
    global switches
    switches += 1

    if switches != 1:
        return dict

    if not dict:  # If the dictionary is empty, do nothing
        return

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
    while True:
        drawing = recv(client_socket)
        if drawing != '' and drawing is not None:
            print('found a drawing from player from: ' + str(this_player))
            print(drawing)
            player_dict[this_player] = drawing
            print(player_dict)
            break

    with LOCK_COUNT:
        drawings_count += 1
        print('ready drawings: ' + str(drawings_count))


def receive_sentence(client_socket, player_dict, this_player):
    print('waiting to receive a sentence from player - ' + str(this_player))
    global count
    while True:
        sentence = recv(client_socket)
        if sentence != '' and sentence is not None:
            print('found a sentence from player: ' + sentence + ', from: ' + str(this_player))
            player_dict[this_player] = sentence
            break

    with LOCK_COUNT:
        count += 1
        print('ready sentences: ' + str(count))


def send_sentence(client_socket, player_dict, this_player):
    global send_sentence_count
    print('waiting to player request for sentence - ' + str(this_player))
    while True:
        request = recv(client_socket)
        if request == "give sentence":
            print("sending the sentence: " + str(player_dict[this_player]) + " to player: " + str(this_player))
            send(client_socket, player_dict[this_player])
            break
    with LOCK_COUNT:
        send_sentence_count += 1
        print('ready sentences: ' + str(count))


def send_drawings(client_socket, player_dict_drawing, this_player):
    print('waiting to player request for drawing - ' + str(this_player))
    while True:
        request = recv(client_socket)
        if request == "give drawing":
            print("sending the drawing to player: " + str(this_player))
            send(client_socket, player_dict_drawing[this_player])
            break


def handle_connection(client_socket, player_dict, this_player):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        wait_for_ready(client_socket)
        while True:
            with LOCK_COUNT:
                if 2 <= len(player_dict) == ready_count:
                    break
        send(client_socket, 'game started')

        receive_sentence(client_socket, player_dict, this_player)
        # checks if everyone has sent their sentence

        while count != len(player_dict):
            pass

        send(client_socket, 'start drawing')

        print('circular switch check')
        player_dict = circular_switch(player_dict)
        print(str(player_dict))

        global send_sentence_count
        send_sentence(client_socket, player_dict, this_player)
        while len(player_dict) != send_sentence_count:
            pass


        print('waiting for receiving drawings')

        player_dict_drawing = player_dict
        receive_drawing(client_socket, player_dict_drawing, this_player)

        while len(player_dict_drawing) != drawings_count:
            pass

        print('received all drawings')

        global switches
        switches = 0
        player_dict_drawing = circular_switch(player_dict_drawing)



        print('done')

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


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
        server_socket.close()


if __name__ == '__main__':
    main()
