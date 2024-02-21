import asyncio
import logging
import time
import traceback

from signalbot import ReceiveMessagesError, UnknownMessageFormatError
from signalbot.bot import SignalBotError
from signalbot.pattern.models.models import Message


class UpdateHandler:
    def __init__(self, signal_api):
        self._signal_api = signal_api
        self._event_loop = asyncio.get_event_loop()
        self._q = asyncio.Queue()

    async def start(self):
        await self._event_loop.create_task(self._produce_consume_messages())

    @classmethod
    async def _rerun_on_exception(cls, coro, *args, **kwargs):
        """Restart coroutine by waiting an exponential time deplay"""
        max_sleep = 5 * 60  # sleep for at most 5 mins until rerun
        reset = 3 * 60  # reset after 3 minutes running successfully
        init_sleep = 1  # always start with sleeping for 1 second

        next_sleep = init_sleep
        while True:
            start_t = int(time.monotonic())  # seconds

            try:
                await coro(*args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception:
                traceback.print_exc()

            end_t = int(time.monotonic())  # seconds

            if end_t - start_t < reset:
                sleep_t = next_sleep
                next_sleep = min(max_sleep, next_sleep * 2)  # double sleep time
            else:
                next_sleep = init_sleep  # reset sleep time
                sleep_t = next_sleep

            logging.warning(f"Restarting coroutine in {sleep_t} seconds")
            await asyncio.sleep(sleep_t)

    async def _produce_consume_messages(self, producers=1, consumers=3) -> None:
        for n in range(1, producers + 1):
            produce_task = self._rerun_on_exception(self._produce, n)
            await asyncio.create_task(produce_task)

        for n in range(1, consumers + 1):
            consume_task = self._rerun_on_exception(self._consume, n)
            await asyncio.create_task(consume_task)

    async def _produce(self, name: int) -> None:
        logging.info(f"[Bot] Producer #{name} started")
        try:
            async for raw_message in self._signal_api.receive():
                logging.info(f"[Raw Message] {raw_message}")

                try:
                    message = Message.parse(raw_message)
                except UnknownMessageFormatError:
                    continue

                await self._q.put(message)

        except ReceiveMessagesError as e:
            # TODO: retry strategy
            raise SignalBotError(f"Cannot receive messages: {e}")

    async def _consume(self, name: int) -> None:
        while True:
            message = await self._q.get()
            # TODO: handle the message