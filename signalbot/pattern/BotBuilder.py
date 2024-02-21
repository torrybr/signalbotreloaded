from abc import  abstractmethod

from signalbot.pattern.Bot import Bot


class BotBuilder:
    def __init__(self):
        self.bot = Bot()

    @abstractmethod
    def set_cli_service_url(self, cli_service_url):
        pass

    @abstractmethod
    def set_phone_number(self, phone_number):
        pass

    @abstractmethod
    def set_storage(self, storage):
        pass

    @abstractmethod
    def add_handler(self, handler):
        pass

    @abstractmethod
    def build(self):
        pass
