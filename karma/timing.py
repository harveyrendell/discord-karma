from datetime import datetime

import tzlocal

TIMESTAMP_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

class Timing():
    timezone = tzlocal.get_localzone()
    start_time = None

    @classmethod
    def start(cls):
        cls.start_time = cls.timezone.localize(datetime.now())
        return cls.start_time

    @classmethod
    def get_uptime(cls):
        if not cls.start_time:
            raise TimingError('Timer has not been started. Cannot get uptime.')

        uptime = Timing.current_time() - cls.start_time
        return uptime

    @classmethod
    def get_uptime_readable(cls):
        uptime = cls.get_uptime()
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        result = '{} Days, {} Hours, {} Minutes, {} Seconds'.format(
            uptime.days,
            hours,
            minutes,
            seconds
        )
        return result

    @classmethod
    def current_time(cls):
        return cls.timezone.localize(datetime.now())

    @staticmethod
    def timestamp(time):
        return time.isoformat()

    @staticmethod
    def human_readable(time):
        return time.strftime(TIMESTAMP_FORMAT)


class TimingError(Exception):
    pass
