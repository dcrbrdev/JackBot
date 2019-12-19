import ssl
import logging
from threading import Thread, Lock

from websocket import WebSocketApp
from mongoengine.errors import ValidationError

from bot.jack import JackBot
from db.subject import Subject
from db.update_message import UpdateMessage
from db.exceptions import DuplicatedUpdateMessageError
from sws.exceptions import DuplicatedSessionError, SessionWebSocketNotFoundError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class SessionWebSocket(Thread):
    sessions = {}
    lock = Lock()

    def __init__(self, subject: Subject):
        self.subject = subject

        super(SessionWebSocket, self).__init__()
        if SessionWebSocket.sessions.get(self.uri):
            raise DuplicatedSessionError(
                f"A session with subject {subject} is already created!")

        SessionWebSocket.sessions[self.uri] = self

        self.ws = None
        self.ignore_next_update = False

    def __str__(self):
        return f"{self.subject}"

    @property
    def name(self):
        return self.subject.name

    @property
    def uri(self):
        return self.subject.uri

    @property
    def header(self):
        return self.subject.header

    def set_ws(self):
        self.ws = WebSocketApp(self.subject.uri,
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
    def on_message(ws: WebSocketApp, data):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.url)
        if not sws.ignore_next_update:
            try:
                msg = UpdateMessage.from_data(sws.subject, data)
                logger.info(f'SessionUpdateMessage received from {sws.name}')
                logger.info(f'{sws.name} trying to acquire lock...')
                sws.lock.acquire()
                logger.info(f'{sws.name} got the lock!')
                sws.subject.notify(msg)
                sws.lock.release()
                logger.info(f'{sws.name} released lock!')
            except (ValidationError, DuplicatedUpdateMessageError) as e:
                logger.info(f"Supress {e} for creating {UpdateMessage} "
                            f"from {data} on {sws}")
        else:
            sws.ignore_next_update = False

    @staticmethod
    def on_error(ws, error: Exception):
        sws: SessionWebSocket = SessionWebSocket.get_sws(ws.uri)
        sws.ignore_next_update = True
        logger.warning(error)

    @classmethod
    def create_all(cls):
        subjects = Subject.objects()
        for subject in subjects:
            cls(subject)

    @classmethod
    def start_all(cls):
        for session in cls.sessions.values():
            session.start()

    @classmethod
    def join_all(cls):
        for session in cls.sessions.values():
            session.join()


if __name__ == "__main__":
    JackBot.instance()
    logger.info("Creating all SWS's...")
    SessionWebSocket.create_all()
    logger.info(f"SWS's created: {SessionWebSocket.sessions}")
    logger.info("Starting all SWS's...")
    SessionWebSocket.start_all()
    logger.info("Joining all SWS's...")
    SessionWebSocket.join_all()
