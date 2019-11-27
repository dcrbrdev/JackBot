import ssl
import logging
from threading import Thread

from websocket import WebSocketApp

from bot.jack import JackBot
from sws.message import UpdateMessage
from sws.exceptions import DuplicatedSessionError, SessionWebSocketNotFoundError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


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
        self.ws = None
        self.ignore_next_update = False

    def set_ws(self):
        self.ws = WebSocketApp(self.url,
                               on_message=self.on_message,
                               on_error=self.on_error)

    def run(self):
        while True:
            self.set_ws()
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    @classmethod
    def get_sws(cls, url):
        sws: SessionWebSocket = SessionWebSocket.sessions.get(url)
        if sws is None:
            raise SessionWebSocketNotFoundError(f'A SWS with the url {url} '
                                                f'was not found!')
        return sws

    @staticmethod
    def on_message(ws: WebSocketApp, msg):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.url)
        if not sws.ignore_next_update:
            msg = UpdateMessage.from_msg(sws.name, msg)
            logger.info(f'SessionUpdateMessage received from {msg.sws_name}')
            JackBot.instance().send_message(f'{msg}', parse_mode='HTML')
        else:
            sws.ignore_next_update = False

    @staticmethod
    def on_error(ws, error: Exception):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.url)
        sws.ignore_next_update = True
        logger.warning(error)

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
