import logging

from commands import (
    PingCommand,
    ReplyCommand,
)
from signalbot.bot import SignalBot

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.WARNING)


def main():
    signal_service = "localhost:8080"
    phone_number = "+15157838691"

    config = {
        "signal_service": signal_service,
        "phone_number": phone_number,
    }
    bot = SignalBot(config)

    # enable a chat command for all contacts and all groups
    bot.register(PingCommand())
    bot.register(ReplyCommand())

    # enable a chat command only for groups
    # bot.register(FridayCommand(), contacts=False, groups=True)
    #
    # # enable a chat command for one specific group with the name "My Group"
    # bot.register(TypingCommand(), groups=["My Group"])
    #
    # # chat command is enabled for all groups and one specific contact
    # bot.register(TriggeredCommand(), contacts=["+490123456789"], groups=True)

    bot.start()


if __name__ == "__main__":
    main()
