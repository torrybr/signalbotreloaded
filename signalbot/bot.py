import asyncio
import logging
import time
import traceback
from collections import defaultdict
from typing import Optional, Union, List, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .api import SignalAPI, ReceiveMessagesError
from .command import Command
from .context import Context
from .errors import UnknownMessageFormatError, SignalBotError
from .models import Message, Reaction, SendMessage
from .storage.base_storage import BaseStorage
from .storage.memory_storage import InMemoryStorage
from .utils.util_functions import is_phone_number, is_group_id


class SignalBot:
    def __init__(self, config: dict, storage: BaseStorage = InMemoryStorage()):
        """SignalBot

        Example Config:
        ===============
        signal_service: "127.0.0.1:8080"
        phone_number: "+49123456789"
        storage:
            redis_host: "redis"
            redis_port: 6379
        """
        self.config = config

        self.storage = storage

        self.commands = []  # populated by .register()

        self.groups = []  # populated by .register()
        self._groups_by_id = {}
        self._groups_by_internal_id = {}
        self._groups_by_name = defaultdict(list)

        try:
            self._phone_number = self.config['phone_number']
            self._signal_service = self.config['signal_service']
            self._signal = SignalAPI(self._signal_service, self._phone_number)
        except KeyError:
            raise SignalBotError(
                'Could not initialize SignalAPI with given config'
            )

        self._event_loop = asyncio.get_event_loop()
        self._q = asyncio.Queue()

        try:
            self.scheduler = AsyncIOScheduler(event_loop=self._event_loop)
        except Exception as e:
            raise SignalBotError(f'Could not initialize scheduler: {e}')

    def register(
        self,
        command: Command,
        contacts: Optional[Union[List[str], bool]] = True,
        groups: Optional[Union[List[str], bool]] = True,
        f: Optional[Callable[[Message], bool]] = None,
    ):
        command.bot = self
        command.setup()

        group_ids = None

        if isinstance(groups, bool):
            group_ids = groups

        if isinstance(groups, list):
            group_ids = []
            for group in groups:
                if is_group_id(group):  # group is a group id, higher prio
                    group_ids.append(group)
                else:  # group is a group name
                    for matched_group in self._groups_by_name:
                        group_ids.append(matched_group['id'])

        self.commands.append((command, contacts, group_ids, f))

    def start(self):
        # TODO: schedule this every hour or so
        self._event_loop.create_task(self._detect_groups())
        self._event_loop.create_task(self._produce_consume_messages())

        # Add more scheduler tasks here
        # self.scheduler.add_job(...)
        self.scheduler.start()

        # Run event loop
        self._event_loop.run_forever()

    async def send(
        self, receiver: str, send_message_object: SendMessage
    ) -> None:
        receiver_resolved = self._resolve_receiver(receiver)
        send_message_object.recipients = [receiver_resolved]
        resp = await self._signal.send_message(message=send_message_object)

        resp_payload = await resp.json()
        timestamp = resp_payload['timestamp']
        logging.info(
            f'[Bot] New message {timestamp} sent:\n{send_message_object.message}'
        )

    async def react(self, message: Message, emoji: str) -> None:
        # TODO: check that emoji is really an emoji
        recipient = self._resolve_receiver(message.recipient())
        # I doubt this should be the message timestamp .. should be the time sent
        reaction = Reaction(
            recipient=recipient,
            emoji=emoji,
            target_author=message.source,
            timestamp=message.timestamp,
        )
        await self._signal.react(reaction)
        logging.info(f'[Bot] New reaction: {emoji}')

    async def start_typing(self, receiver: str) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.start_typing(receiver)

    async def stop_typing(self, receiver: str) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.stop_typing(receiver)

    async def _detect_groups(self) -> None:
        # reset group lookups to avoid stale data
        self.groups = await self._signal.get_groups()

        self._groups_by_id = {}
        self._groups_by_internal_id = {}
        self._groups_by_name = defaultdict(list)
        for group in self.groups:
            self._groups_by_id[group['id']] = group
            self._groups_by_internal_id[group['internal_id']] = group
            self._groups_by_name[group['name']].append(group)

        logging.info(f'[Bot] {len(self.groups)} groups detected')

    def _resolve_receiver(self, receiver: str) -> str:
        if is_phone_number(receiver):
            return receiver

        if is_group_id(receiver):
            return receiver

        try:
            group_id = self._groups_by_internal_id[receiver]['id']
            return group_id

        except Exception:
            raise SignalBotError('Cannot resolve receiver.')

    # see https://stackoverflow.com/questions/55184226/catching-exceptions-in-individual-tasks-and-restarting-them
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
                next_sleep = min(
                    max_sleep, next_sleep * 2
                )  # double sleep time
            else:
                next_sleep = init_sleep  # reset sleep time
                sleep_t = next_sleep

            logging.warning(f'Restarting coroutine in {sleep_t} seconds')
            await asyncio.sleep(sleep_t)

    async def _produce_consume_messages(
        self, producers=1, consumers=3
    ) -> None:
        for n in range(1, producers + 1):
            produce_task = self._rerun_on_exception(self._produce, n)
            await asyncio.create_task(produce_task)

        for n in range(1, consumers + 1):
            consume_task = self._rerun_on_exception(self._consume, n)
            await asyncio.create_task(consume_task)

    async def _produce(self, name: int) -> None:
        logging.info(f'[Bot] Producer #{name} started')
        try:
            async for raw_message in self._signal.receive():
                logging.info(f'[Raw Message] {raw_message}')

                try:
                    message = Message.parse(raw_message)
                except UnknownMessageFormatError:
                    continue

                await self._ask_commands_to_handle(message)

        except ReceiveMessagesError as e:
            # TODO: retry strategy
            raise SignalBotError(f'Cannot receive messages: {e}')

    def _should_react_for_contact(
        self,
        message: Message,
        contacts: bool,
        group_ids: list[str],
    ):
        """Is the command activated for a certain chat or group?"""

        # Case 1: Private message
        if message.is_private():
            # a) registered for all numbers
            if isinstance(contacts, bool) and contacts:
                return True

            # b) whitelisted numbers
            if isinstance(contacts, list) and message.source in contacts:
                return True

        # Case 2: Group message
        if message.is_group():
            # a) registered for all groups
            if isinstance(group_ids, bool) and group_ids:
                return True

            # b) whitelisted group ids
            group_id = self._groups_by_internal_id.get(message.group, {}).get(
                'id'
            )
            if (
                isinstance(group_ids, list)
                and group_id
                and group_id in group_ids
            ):
                return True

        return False

    def _should_react_for_lambda(
        self,
        message: Message,
        f: None,
    ) -> bool:
        if f is None:
            return True

        return f(message)

    async def _ask_commands_to_handle(self, message: Message):
        for command, contacts, group_ids, f in self.commands:
            if not self._should_react_for_contact(
                message, contacts, group_ids
            ):
                continue

            if not self._should_react_for_lambda(message, f):
                continue

            await self._q.put((command, message, time.perf_counter()))

    async def _consume(self, name: int) -> None:
        logging.info(f'[Bot] Consumer #{name} started')
        while True:
            try:
                await self._consume_new_item(name)
            except Exception:
                continue

    async def _consume_new_item(self, name: int) -> None:
        command, message, t = await self._q.get()
        now = time.perf_counter()
        logging.info(
            f'[Bot] Consumer #{name} got new job in {now - t:0.5f} seconds'
        )

        # handle Command
        try:
            context = Context(self, message)
            await command.handle(context)
        except Exception as e:
            logging.error(f'[{command.__class__.__name__}] Error: {e}')
            raise e

        # done
        self._q.task_done()
