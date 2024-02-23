class UnknownMessageFormatError(Exception):
    pass


class ReceiveMessagesError(Exception):
    pass


class SendMessageError(Exception):
    pass


class TypingError(Exception):
    pass


class StartTypingError(TypingError):
    pass


class StopTypingError(TypingError):
    pass


class ReactionError(Exception):
    pass


class GroupsError(Exception):
    pass


class StorageError(Exception):
    pass


class SignalBotError(Exception):
    pass


class CommandError(Exception):
    pass
