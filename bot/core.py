import logging
from abc import ABC, abstractmethod

from decouple import config
from telegram.ext import Updater, Handler
from telegram import Update, ParseMode, TelegramError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class BotTelegramCore(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            BotTelegramCore._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        logger.info('Initializing bot...')
        self.token = config('BOT_TOKEN')
        self.port = config('PORT', default=-1, cast=int)
        self.server_url = config('SERVER_URL', default='?MY_CUSTOM_URL?')

        self._updater = Updater(self.token, use_context=True)
        self._running = False

    @classmethod
    def instance(cls):
        return cls._instance or cls()

    @abstractmethod
    def config_handlers(self):
        raise NotImplementedError(
            'Cannot call config_handler from BotTelegramCore'
        )

    @property
    @abstractmethod
    def chat_id(self):
        raise NotImplementedError(
            'Cannot call chat_id from BotTelegramCore'
        )

    @property
    def chat(self):
        return self.get_chat(self.chat_id)

    def get_chat(self, chat_id):
        return self._updater.bot.get_chat(chat_id)

    def is_from_official_chat(self, update: Update):
        return self.chat_id == update.message.chat.id

    @staticmethod
    def get_administrators_ids(chat):
        return [chat_member.user.id for
                chat_member in chat.get_administrators()]

    @classmethod
    def is_admin(cls, user_id, chat_id=None):
        instance = cls.instance()
        try:
            chat = instance.get_chat(chat_id)
        except TelegramError:
            chat = instance.chat
        return chat.type == chat.PRIVATE or user_id in instance.get_administrators_ids(chat)

    @classmethod
    def send_message(cls, text, chat_id, parse_mode=None):
        instance = cls.instance()
        return instance._updater.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode or ParseMode.HTML
        )

    @classmethod
    def delete_message(cls, chat_id, message_id):
        instance = cls.instance()
        return instance._updater.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )

    @classmethod
    def forward_message(cls, to_chat_id, from_chat_id, message_id):
        instance = cls.instance()
        return instance._updater.bot.forward_message(
            chat_id=to_chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )

    def add_handler(self, handler: Handler):
        if not isinstance(handler, Handler):
            raise ValueError("Handler function must be of type Handler!")
        self._updater.dispatcher.add_handler(handler)

    def add_error_handler(self, handler):
        self._updater.dispatcher.add_error_handler(handler)

    def run_web(self):
        """Start the bot as a webhook server"""

        self._updater.start_webhook(
            listen="0.0.0.0",
            port=self.port,
            url_path=self.token
        )

        self._updater.bot.set_webhook(f"{self.server_url}/{self.token}")

        logger.info('JackBot is running as a webserver!')
        self._updater.idle()

    def run_cmd(self):
        """Start the bot as a python script loop"""
        self._updater.start_polling()

        logger.info('JackBot is running as python script!')
        self._updater.idle()
