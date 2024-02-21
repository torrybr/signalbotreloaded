from abc import ABC

from signalbot import SignalAPI
from signalbot.pattern.BotBuilder import BotBuilder
from signalbot.pattern.storage import BaseStorage


class ConcreteBotBuilder(BotBuilder, ABC):
    def set_name(self, name):
        self.bot.name = name
        return self

    def set_phone_number(self, phone_number):
        self.bot.phone_number = phone_number
        self.check_and_set_signal_api()

    def set_cli_service_url(self, cli_service_url):
        self.bot.cli_service_url = cli_service_url
        self.check_and_set_signal_api()
        return self

    def set_storage(self, storage: BaseStorage):
        self.bot.storage = storage
        return self

    def add_handler(self, handler):
        self.bot.handlers.append(handler)
        return self

    def set_group_chats(self, group_chats):
        self.bot.group_chats = group_chats
        return self

    def set_signal_api(self, signal_api):
        self.bot._signal_api = signal_api
        return self

    def build(self):
        return self.bot

    def check_and_set_signal_api(self):
        if self.bot.phone_number and self.bot.cli_service_url:
            self.bot._signal_api = SignalAPI(self.bot.phone_number, self.bot.cli_service_url)

    def start(self):
        self.bot.start()
