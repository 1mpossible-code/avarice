import sys
import telebot
from telebot import types
import bot_functions as bf
from configloader import config
import logging

# Trying to import colored logs
try:
    import coloredlogs

    logs_level_styles = dict(
        spam=dict(color=22, faint=True),
        debug=dict(color=28),
        verbose=dict(color='blue'),
        info=dict(),
        notice=dict(color=220),
        warning=dict(color=202),
        success=dict(color=118, bold=True),
        error=dict(color=124),
        critical=dict(background='red', bold=True),
    )
except ImportError:
    coloredlogs = None


def main():
    """The core code of the program"""
    # Logs initialization
    log = logging.getLogger(__name__)
    logging.root.setLevel(config["Logging"]["level"])
    stream_handler = logging.StreamHandler()
    if coloredlogs is not None:
        stream_handler.formatter = coloredlogs.ColoredFormatter(config["Logging"]["format"], style="{",
                                                                level_styles=logs_level_styles)
    else:
        stream_handler.formatter = logging.Formatter(config["Logging"]["format"], style="{")
    logging.root.handlers.clear()
    logging.root.addHandler(stream_handler)
    log.debug("Logging setup successfully!")

    # Ignore most python-telegram-bot logs, as they are useless most of the time
    logging.getLogger("urllib3.connectionpool").setLevel("ERROR")
    # logging.getLogger("Telegram").setLevel("ERROR")

    # Trying to connect with the Telegram bot by the token
    try:
        bot = telebot.TeleBot(config["Telegram"]["token"])
        bot.get_me()
        log.debug('Connection to the bot was successful!')
    except telebot.apihelper.ApiException:
        log.error('A request to the Telegram API was unsuccessful.')
        log.fatal('Write the valid token in the config file and restart the script')
        sys.exit(1)
    log.debug("Bot connection is valid!")

    log.info("avarice is started!")

    @bot.message_handler(commands=["start"])
    def start(message):
        bf.sending_start_message(bot, message, types)
        bf.start_func(message)

    @bot.message_handler(commands=["help"])
    def helping(message):
        bf.sending_help_message(bot, message)

    @bot.message_handler(content_types=["text"])
    def message_handler(message):
        if message.chat.type == 'private':
            bf.handler(bot, types, message, None)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        bf.handler(bot, types, None, call)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
