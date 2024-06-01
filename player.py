

class Player:
    def __init__(self,name, socket,address):
        self.name = name
        self.socket = socket
        self.address = address
        self.sentence = ''

    def __repr__(self):
        return f"<Player name: {self.name}>"
