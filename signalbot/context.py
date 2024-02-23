# from .bot import Signalbot # TODO: figure out how to enable this for typing
from .models import Message, SendMessage


class Context:
    def __init__(self, bot, message: Message):
        self.bot = bot
        self.message = message

    async def send(
        self,
        text: str,
        base64_attachments: list = None,
        mentions: list = None,
        text_mode: str = None,
    ):

        send_message_object = SendMessage(
            message=text,
            number=self.message.recipient(),
            base64_attachments=base64_attachments,
            mentions=mentions,
            text_mode=text_mode,
        )
        return await self.bot.send(
            receiver=self.message.recipient(), message=send_message_object
        )

    async def reply(
        self,
        text: str,
        base64_attachments: list = None,
        mentions: list = None,
        text_mode: str = None,
    ):

        send_message_object = SendMessage(
            message=text,
            number=self.message.recipient(),
            quote_author=self.message.source,
            quote_mentions=self.message.mentions,
            quote_message=self.message.text,
            quote_timestamp=self.message.timestamp,
            base64_attachments=base64_attachments,
            mentions=mentions,
            text_mode=text_mode,
        )

        return await self.bot.send(
            receiver=self.message.recipient(), message=send_message_object
        )

    async def react(self, emoji: str):
        await self.bot.react(self.message, emoji)

    async def start_typing(self):
        await self.bot.start_typing(self.message.recipient())

    async def stop_typing(self):
        await self.bot.stop_typing(self.message.recipient())
