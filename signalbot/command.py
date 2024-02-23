import functools

from signalbot.context import Context


def triggered(*by, case_sensitive=False):
    def decorator_triggered(func):
        @functools.wraps(func)
        async def wrapper_triggered(*args, **kwargs):
            c = args[1]
            text = c.message.text
            if not isinstance(text, str):
                return

            by_words = by
            if not case_sensitive:
                text = text.lower()
                by_words = [t.lower() for t in by_words]
            if text not in by_words:
                return

            return await func(*args, **kwargs)

        return wrapper_triggered

    return decorator_triggered


class Command:
    # optional
    def setup(self):
        pass

    # optional
    def describe(self) -> None:
        return None

    # overwrite
    async def handle(self, context: Context):
        raise NotImplementedError
