import logging
import socket

logging.basicConfig(filename='my_log.log', level=logging.DEBUG)

IP = '127.0.0.1'
PORT = 16241
QUEUE_LEN = 1
MAX_PACKET = 1024
SHORT_SIZE = 2


def main():
    """
    Initializes and manages the socket server.

    :return: None
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.bind(('127.0.0.1', PORT))
        my_socket.listen(QUEUE_LEN)
        logging.debug('waiting for connection...')
        while True:
            client_socket, client_address = my_socket.accept()
            response = ''
            try:
                while response != 'exit':
                    request = Protocol.receive_(client_socket)
                    logging.debug('server received: ' + str(request))
                    response = return_answer(request, client_socket)
            except socket.error as err:
                logging.debug('received socket error on client socket' + str(err))
            finally:
                client_socket.close()
                logging.debug('user disconnected')
    except socket.error as err:
        logging.error('received socket error on server socket' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    main()
