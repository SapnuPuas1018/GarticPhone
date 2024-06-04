import socket


def send(connected_socket, msg):
    """
    Send a message over the connected socket.

    :param connected_socket: The connected socket to send the message through.
    :type connected_socket: socket.socket

    :param msg: The message to be sent.
    :type msg: str

    :return: None
    :rtype: None
    """
    # Check if the last characters of the 'msg' string are a space
    msg = msg.strip()

    msg = str(len(msg)) + '!' + ' '.join(msg.split())

    # Encode the modified 'msg' string and send it through the 'connected_socket'
    connected_socket.send(msg.encode())



def recv(connected_socket):
    """
    Receive a message from the connected socket.

    :param connected_socket: The connected socket to receive the message from.
    :type connected_socket: socket.socket

    :return: A list containing the split components of the received message.
    :rtype: list[str]
    """
    length = ''
    while '!' not in length:
        length += connected_socket.recv(1).decode()
    length = length[:-1]

    length = int(length)

    # Receive the message until the expected length is reached
    received_msg = ''
    while len(received_msg) < length:
        received_msg += connected_socket.recv(1).decode()

    # Split the received message using '!!' as the separator
    return received_msg


if __name__ == '__main__':
    pass
