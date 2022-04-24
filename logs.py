from typing import Optional, Any, TYPE_CHECKING

import coloredlogs

if TYPE_CHECKING:
    pass


def init_logging(
        loglvl: str = "DEBUG",
        fmt: Optional[str] = None,
        off_loggers: Optional[list] = None
):
    fmt = fmt or "%(asctime)s %(name)s[%(process)d] %(levelname)s %(" "message)s"
    coloredlogs.install(
        level=loglvl, isatty=True, fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S.%f"
    )

    import logging

    for logger_name in ['multipart', 'multipart.multipart',
                        'matplotlib', 'broker_tools.storage.s3.aio.client', 'websockets.protocol']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    off_loggers = off_loggers or []
    for logger_name in off_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def shorten(value: Any, length: int = 10) -> str:
    value = str(value)
    if len(value) <= length:
        return value

    return f"{value[:length//2]}...{value[-length//2:]}"
