import socket


def send(connected_socket, msg):
    """
    Send a message through a connected socket after formatting it.

    The function trims the message, prefixes it with its length followed by '!',
    and sends it through the given socket.

    :param connected_socket: The connected socket through which the message is to be sent.
    :type connected_socket: socket.socket
    :param msg: The message to be sent.
    :type msg: str

    :return: None
    :rtype: None
    """
    msg = msg.strip()

    msg = str(len(msg)) + '!' + ' '.join(msg.split())

    # Encode the modified 'msg' string and send it through the 'connected_socket'
    connected_socket.send(msg.encode())



def recv(connected_socket):
    """
    Receive a message from a connected socket after extracting its length.

    The function reads the length of the message, then receives and decodes
    the message of the expected length from the given socket.

    :param connected_socket: The connected socket from which the message is to be received.
    :type connected_socket: socket.socket

    :return: The received message.
    :rtype: str
    """
    length = ''
    while '!' not in length:
        length += connected_socket.recv(1).decode()
    length = length[:-1]

    length = int(length)

    # Receive the message until the expected length is reached
    received_msg = ''
    received_msg = connected_socket.recv(length).decode()
    # while len(received_msg) < length:
    #     received_msg += connected_socket.recv(1).decode()

    # Split the received message using '!!' as the separator
    return received_msg


if __name__ == '__main__':
    pass