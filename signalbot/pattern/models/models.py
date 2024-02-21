import json
from typing import Union

from pydantic import BaseModel

from signalbot import UnknownMessageFormatError
from signalbot.pattern.enum.message_type import MessageType


class Group(BaseModel):
    id: str
    internal_id: str
    name: str
    members: list
    admins: list = []
    pending_invites: list = []
    pending_requests: list = []


class Mention(BaseModel):
    author: str
    start: int
    length: int


class Contact(BaseModel):
    number: str
    name: str = None


class Reaction(BaseModel):
    reaction: str
    recipient: str
    target_author: str
    timestamp: int


class Message(BaseModel):
    source: str
    timestamp: int
    type: MessageType
    text: str
    base64_attachments: list = []
    sticker: str = None
    group: str = None
    reaction: str = None
    mentions: list[Mention] = []
    raw_message: str = None
    recipients: list = []

    def recipient(self) -> str:
        if self.group:
            return self.group
        return self.source

    def is_private(self) -> bool:
        return not self.is_group()

    def is_group(self) -> bool:
        return bool(self.group)

    @classmethod
    def parse(cls, raw_message: str):
        try:
            raw_message = json.loads(raw_message)
        except Exception:
            raise UnknownMessageFormatError

        # General attributes
        try:
            source = raw_message["envelope"]["source"]
            timestamp = raw_message["envelope"]["timestamp"]
        except Exception:
            raise UnknownMessageFormatError

        # Option 1: syncMessage
        if "syncMessage" in raw_message["envelope"]:
            type = MessageType.SYNC_MESSAGE
            text = cls._parse_sync_message(raw_message["envelope"]["syncMessage"])
            group = cls._parse_group_information(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            reaction = cls._parse_reaction(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            mentions = cls._parse_mentions(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )

        # Option 2: dataMessage
        elif "dataMessage" in raw_message["envelope"]:
            type = MessageType.DATA_MESSAGE
            text = cls._parse_data_message(raw_message["envelope"]["dataMessage"])
            group = cls._parse_group_information(raw_message["envelope"]["dataMessage"])
            reaction = cls._parse_reaction(raw_message["envelope"]["dataMessage"])
            mentions = cls._parse_mentions(raw_message["envelope"]["dataMessage"])

        else:
            raise UnknownMessageFormatError

        # TODO: base64_attachments
        base64_attachments = []

        return cls(number=None, source=source, timestamp=timestamp, type=type, text=text,
                   base64_attachments=base64_attachments, sticker=None, group=group, reaction=reaction,
                   mentions=mentions, raw_message=raw_message, recipients=None)

    @classmethod
    def _parse_sync_message(cls, sync_message: dict) -> str:
        try:
            text = sync_message["sentMessage"]["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_data_message(cls, data_message: dict) -> str:
        try:
            text = data_message["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_group_information(self, message: dict) -> Union[str, None]:
        ### should return a GROUP object not a str
        try:
            group = message["groupInfo"]["groupId"]
            return group
        except Exception:
            return None

    @classmethod
    def _parse_mentions(cls, data_message: dict) -> list[Mention]:
        try:
            mentions = data_message["mentions"]
            return mentions
        except Exception:
            return []

    @classmethod
    def _parse_reaction(self, message: dict) -> Union[str, None]:
        try:
            reaction = message["reaction"]["emoji"]
            return reaction
        except Exception:
            return None
