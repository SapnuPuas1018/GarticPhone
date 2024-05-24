import logging
import socket
from threading import Thread
from player import Player

logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)


IP = '127.0.0.1'
PORT = 5555
QUEUE_LEN = 20
MAX_PACKET = 1024

player_list = []
ready_count = 0


def send_to_everyone(player_list, data):
    for sock in player_list:
        sock.socket.sendall(data.encode())


def is_everyone_ready(client_socket, player_list):
    global ready_count
    is_ready = client_socket.recv(MAX_PACKET).decode()
    print(is_ready)

    if is_ready == 'True':
        ready_count += 1
    else:
        ready_count -= 1

    print(ready_count)
    if 2 <= len(player_list) == ready_count:
        send_to_everyone(player_list, 'game started')
        return True


def handle_connection(client_socket, player_list):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        ok = False
        while not ok:
            ok = is_everyone_ready(client_socket, player_list)

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

        player_list = []
        while True:
            client_socket, client_address = server_socket.accept()
            print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))
            name = client_socket.recv(MAX_PACKET).decode()
            player_list.append(Player(name, client_socket, client_address))
            print(player_list)
            thread = Thread(target=handle_connection,
                            args=(client_socket, player_list))
            thread.start()

    except socket.error as err:
        logging.error('received socket error on server socket' + str(err))
        print('received socket error on client socket' + str(err))

    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
