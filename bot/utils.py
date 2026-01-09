from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def day_suffix(day: int) -> str:
    if not 1 <= day <= 31:
        raise ValueError("Day must be in range 1-31")
    match day:
        case 1 | 21 | 31:
            return "st"
        case 2 | 22:
            return "nd"
        case 3 | 23:
            return "rd"
        case _:
            return "th"


def format_day(day: int) -> str:
    return f"{day}{day_suffix(day)}"


def format_date(date: datetime) -> str:
    return f"{date.strftime('%B')} {format_day(date.day)}"
