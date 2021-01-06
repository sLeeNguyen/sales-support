import pytz
from django.conf import settings


TIME_ZONE = settings.TIME_ZONE


def server_timezone(datetime):
    return datetime.astimezone(pytz.timezone(TIME_ZONE))


def client_timezone(datetime, timezone=None):
    if timezone is None:
        return server_timezone(datetime)
    return datetime.astimezone(pytz.timezone(timezone))
