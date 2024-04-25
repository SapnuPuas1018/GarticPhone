import logging
import socket
from _thread import *
logging.basicConfig(filename='my_log_server.log', level=logging.DEBUG)


IP = '127.0.0.1'
PORT = 5555
QUEUE_LEN = 20
MAX_PACKET = 1024
SHORT_SIZE = 2


def threaded_client(client_socket):
    try:
        response = ''
        while True:
            data = client_socket.recv(MAX_PACKET)
            response = data.decode()
            if not data:
                logging.debug('disconnected')
                print('disconnected')
                break
            else:
                print('received: ', response)
                print('sending: ', response)
            client_socket.send(str.encode(data))
    except socket.error as err:
        logging.debug('received error: ' + str(err))
        print('received error: ' + str(err))

def main():
    """
    Initializes and manages the socket server.

    :return: None
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.bind((IP, PORT))
        my_socket.listen(QUEUE_LEN)
        logging.debug('waiting for connection...')
        print('waiting for connection...')
        while True:
            client_socket, client_address = my_socket.accept()
            logging.debug('connected to: ' + client_address)
            print('connected to: ' + client_address)
            start_new_thread(threaded_client, (client_socket,))
        try:

        except socket.error as err:
            logging.debug('received socket error on client socket' + str(err))
            print('received socket error on client socket' + str(err))
        finally:
            client_socket.close()
            logging.debug('user disconnected')
    except socket.error as err:
        logging.error('received socket error on server socket' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    main()
