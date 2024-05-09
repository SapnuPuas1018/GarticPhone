import logging
import socket
from threading import Thread
logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)


IP = '127.0.0.1'
PORT = 5555
QUEUE_LEN = 20
MAX_PACKET = 1024
player_list = []


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))
        name = client_socket.recv(MAX_PACKET).decode()
        print(name)
        player_list.append(name)
        print(player_list)
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
        while True:
            client_socket, client_address = server_socket.accept()
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()

    except socket.error as err:
        logging.error('received socket error on server socket' + str(err))
        print('received socket error on client socket' + str(err))

    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
