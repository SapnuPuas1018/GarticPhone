

class Player:
    def __init__(self, name, socket, address):
        self.name = name
        self.socket = socket
        self.address = address
        self.is_ready = False
        self.sentence = ''
        self.drawing = ''

    def __repr__(self):
        return f"<Player name: {self.name}>"
