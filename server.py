import logging
import socket
import threading
from threading import Thread
from player import Player

logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)


IP = '127.0.0.1'
PORT = 5556
QUEUE_LEN = 20
MAX_PACKET = 1024
LOCK_COUNT = threading.Lock()


player_dict = []
ready_count = 0
count = 0


def send_to_everyone(player_dict, data):
    for sock in player_dict:
        sock.socket.send(data.encode())


def how_many_ready(client_socket):
    global ready_count
    is_ready = client_socket.recv(MAX_PACKET).decode()
    with LOCK_COUNT:
        print('ready_count:' + str(ready_count))
        if is_ready == 'True':
            ready_count += 1
        else:
            ready_count -= 1


def receive_sentence(client_socket, player_dict, this_player):
    print('kaka')
    global count
    while True:
        sentence = client_socket.recv(MAX_PACKET).decode()
        print('sentence: ' + sentence)
        if sentence != '' and sentence is not None:
            break

    player_dict[this_player] = sentence
    with LOCK_COUNT:
        count += 1
        print('count: ' + str(count))

    print(sentence)

    print(player_dict)


def handle_connection(client_socket, player_dict, this_player):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        how_many_ready(client_socket)
        while True:
            with LOCK_COUNT:
                if 2 <= len(player_dict) == ready_count:
                    break
        client_socket.send('game started'.encode())

        print('done')

        receive_sentence(client_socket, player_dict, this_player)
        # checks if everyone has sent their sentence
        while True:
            with LOCK_COUNT:
                if count == len(player_dict):
                    break
        client_socket.send('idk'.encode())

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
            name = client_socket.recv(MAX_PACKET).decode()
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