from enum import Enum, auto


class MessageType(Enum):
    SYNC_MESSAGE = auto()
    DATA_MESSAGE = auto()
    AUDIO_CALL = auto()
