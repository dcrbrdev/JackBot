from bot.commands.base import config_handlers as base_handlers
from bot.commands.subscription import config_handlers as subscription_handlers
from bot.commands.callback import config_handlers as callback_handlers
from bot.commands.exchange import config_handlers as exchange_handlers
from bot.commands.subject import config_handlers as subject_handlers

handlers = [
    base_handlers,
    subscription_handlers,
    callback_handlers,
    exchange_handlers,
    subject_handlers
]
