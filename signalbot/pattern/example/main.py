from signalbot.pattern.ConcreteBotBuilder import ConcreteBotBuilder


def main():
    # signal_service = os.environ["SIGNAL_SERVICE"]
    # phone_number = os.environ["PHONE_NUMBER"]
    #
    # config = {
    #     "signal_service": signal_service,
    #     "phone_number": phone_number,
    #     "storage": None,
    # }
    # bot = SignalBot(config)
    #
    # # enable a chat command for all contacts and all groups
    # bot.register(PingCommand())
    # bot.register(ReplyCommand())
    #
    # # enable a chat command only for groups
    # bot.register(FridayCommand(), contacts=False, groups=True)
    #
    # # enable a chat command for one specific group with the name "My Group"
    # bot.register(TypingCommand(), groups=["My Group"])
    #
    # # chat command is enabled for all groups and one specific contact
    # bot.register(TriggeredCommand(), contacts=["+490123456789"], groups=True)

    bot_builder = ConcreteBotBuilder()

    bot_builder.set_name("SignalBot")
    bot_builder.set_phone_number("+15157838691")

    bot_builder.start()


if __name__ == "__main__":
    main()
