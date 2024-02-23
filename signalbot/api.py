import aiohttp
import websockets
from aiohttp import ClientResponse

from signalbot.errors import (
    GroupsError,
    StopTypingError,
    StartTypingError,
    SendMessageError,
    ReactionError,
    ReceiveMessagesError,
)
from signalbot.models import Group, Reaction, SendMessage, TypingIndicator


class SignalAPI:
    def __init__(
        self,
        signal_service: str,
        phone_number: str,
    ):
        self.signal_service = signal_service
        self.phone_number = phone_number
        self.connection = None

    async def receive(self):
        try:
            uri = self._receive_ws_uri()
            self.connection = websockets.connect(uri, ping_interval=None)
            async with self.connection as websocket:
                async for raw_message in websocket:
                    yield raw_message

        except Exception as e:
            raise ReceiveMessagesError(e)

    async def send_message(self, message: SendMessage) -> ClientResponse:
        uri = self._send_rest_uri()

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(uri, json=message)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
            KeyError,
        ):
            raise SendMessageError

    async def react(self, reaction: Reaction) -> ClientResponse:
        uri = self._react_rest_uri()
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(uri, json=reaction)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise ReactionError

    async def start_typing(self, receiver: str) -> ClientResponse:
        uri = self._typing_indicator_uri()
        payload = TypingIndicator(recipient=receiver)
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.put(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StartTypingError

    async def stop_typing(self, receiver: str) -> ClientResponse:
        uri = self._typing_indicator_uri()
        payload = TypingIndicator(recipient=receiver)
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.delete(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StopTypingError

    async def get_groups(self) -> list[Group]:
        uri = self._groups_uri()
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(uri)
                resp.raise_for_status()
                return await resp.json()
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise GroupsError

    def _receive_ws_uri(self):
        return f'ws://{self.signal_service}/v1/receive/{self.phone_number}'

    def _send_rest_uri(self):
        return f'http://{self.signal_service}/v2/send'

    def _react_rest_uri(self):
        return f'http://{self.signal_service}/v1/reactions/{self.phone_number}'

    def _typing_indicator_uri(self):
        return f'http://{self.signal_service}/v1/typing-indicator/{self.phone_number}'

    def _groups_uri(self):
        return f'http://{self.signal_service}/v1/groups/{self.phone_number}'
