import asyncio

from signalbot.pattern.UpdateHandler import UpdateHandler
from signalbot.pattern.models.models import Group
from signalbot.pattern.storage.SqliteStorage import SqliteStorage


class Bot:
    """
    The Bot PRODUCT
    """

    def __init__(self):
        self.name = None
        self.cli_service_url = "localhost:8080"
        self.phone_number = None
        self.storage = SqliteStorage("signalbot.db")
        self.handlers = []
        self._signal_api = None
        self.groups: list[Group] = []

        # This is a problem becuase the user has to set the phone and service url before the bot can start
        self.update_handler = UpdateHandler(self._signal_api)

        self._event_loop = asyncio.get_event_loop()
        self._q = asyncio.Queue()

    def start(self):
        self._event_loop.create_task(self._detect_groups())
        self._event_loop.create_task(self.update_handler.start())

    def say_hi(self):
        print(f"Hi, I am {self.name}")

    def say_bye(self):
        print(f"Bye, I am {self.name}")

    async def _detect_groups(self) -> None:
        if not self._signal_api:
            raise ValueError("Signal API is not set")

        # reset group lookups to avoid stale data
        # BUild a group class to hold the groups
        self.groups = await self._signal_api.get_groups()