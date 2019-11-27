from threading import Thread

from websocket import WebSocketApp

from bot.jack import JackBot
from sws.message import SessionUpdateMessage
from sws.exceptions import DuplicatedSessionError, SessionWebSocketNotFoundError


class SessionWebSocket(Thread):
    sessions = {}

    def __init__(self, name, url):
        super(SessionWebSocket, self).__init__()
        if SessionWebSocket.sessions.get(url):
            raise DuplicatedSessionError("A session with "
                                         "this urls is already created!")
        SessionWebSocket.sessions[url] = self

        self.name = name
        self.url = url
        self.ws = WebSocketApp(self.url, on_message=self.on_message, on_error=self.on_error)

    def parse_message(self, message):
        return SessionUpdateMessage.from_data(self.name, message)

    def run(self):
        self.ws.run_forever()

    @classmethod
    def get_sws(cls, url):
        sws: SessionWebSocket = SessionWebSocket.sessions.get(url)
        if sws is None:
            raise SessionWebSocketNotFoundError(f'A SWS with the url {url} was not found!')
        return sws

    @staticmethod
    def on_message(ws: WebSocketApp, msg):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.url)
        msg = SessionUpdateMessage.from_data(sws.name, msg)
        JackBot.instance().send_message(f'{msg}', parse_mode='HTML')

    @staticmethod
    def on_error(ws, error):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.url)
        print(f'A error ocurred on {sws}:\n{error}')

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
