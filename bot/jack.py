import logging

from decouple import config

from bot.core import BotTelegramCore
from bot.commands import handlers


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class JackBot(BotTelegramCore):
    """Bot Controller"""

    _chat_id = config('JACK_CHAT_ID', default='123')

    def __init__(self):
        super(JackBot, self).__init__()
        self._handlers_configured = False
        self.config_handlers()

    def config_handlers(self):
        for config_handler in handlers:
            config_handler(self)
        self._handlers_configured = True

    @property
    def chat_id(self):
        return self._chat_id

    @classmethod
    def send_message(cls, text, chat_id=None, parse_mode=None):
        super().send_message(text, chat_id or cls._chat_id, parse_mode)


if __name__ == "__main__":
    JackBot.instance().run()
