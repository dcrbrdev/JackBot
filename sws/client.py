from threading import Thread

from websocket import create_connection

from bot.jack import JackBot
from sws.message import SessionUpdateMessage
from sws.exceptions import DuplicatedSessionError


class SessionWebSocket(Thread):
    sessions = {}
    TEN_YEARS_TIMEOUT = 60 * 60 * 24 * 365 * 10

    def __init__(self, name, url):
        super(SessionWebSocket, self).__init__()
        if SessionWebSocket.sessions.get(url):
            raise DuplicatedSessionError("A session with "
                                         "this urls is already created")
        SessionWebSocket.sessions[url] = self

        self.name = name
        self.url = url
        self.ws = create_connection(self.url, timeout=self.TEN_YEARS_TIMEOUT)

    def parse_message(self, message):
        return SessionUpdateMessage.from_data(self.name, message)

    def recv(self):
        msg = SessionUpdateMessage.from_data(self.name, self.ws.recv())
        JackBot.instance().send_message(f'{msg}', parse_mode='HTML')

    def run(self):
        while True:
            self.recv()

    @classmethod
    def start_all(cls):
        for session in cls.sessions.values():
            session.start()

    @classmethod
    def join_all(cls):
        for session in cls.sessions.values():
            session.join()


if __name__ == "__main__":
    SessionWebSocket("Decred Brasil",
                     "wss://split-ticket-svc.stake."
                     "decredbrasil.com:8477/watchWaitingList")
    SessionWebSocket("Decred Voting",
                     "wss://matcher.decredvoting.com:8477/watchWaitingList")
    SessionWebSocket.start_all()
    SessionWebSocket.join_all()
