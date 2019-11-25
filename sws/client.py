from websocket import create_connection

from sws import SessionUpdateMessage


class SessionWebSocket:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.ws = create_connection(self.url)

    def parse_message(self, message):
        return SessionUpdateMessage.from_data(self.name, message)

    def recv(self):
        msg = SessionUpdateMessage.from_data(self.name, self.ws.recv())
        print(msg)

    def run_forever(self):
        while True:
            self.recv()


if __name__ == "__main__":
    sws = SessionWebSocket("Decred Brasil", "wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList")
    sws.run_forever()
