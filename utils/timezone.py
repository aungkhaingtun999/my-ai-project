# ==========================================
# utils/timezone.py
# Enterprise Time Engine
# ==========================================

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config import (
    DEFAULT_TIMEZONE,
    DATETIME_FORMAT
)



def utc_now():

    """
    Database Standard Time
    """

    return datetime.now(
        timezone.utc
    )



def local_now(
    tz=None
):

    """
    Convert UTC to Local Time
    """

    if not tz:

        tz = DEFAULT_TIMEZONE


    return utc_now().astimezone(
        ZoneInfo(tz)
    )



def format_datetime(
    tz=None
):

    return local_now(tz).strftime(
        DATETIME_FORMAT
    )



def format_date(
    tz=None
):

    return local_now(tz).strftime(
        "%d-%m-%Y"
    )



def format_time(
    tz=None
):

    return local_now(tz).strftime(
        "%H:%M:%S"
    )