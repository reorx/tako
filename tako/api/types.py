from pydantic import BaseModel, ConfigDict


class BaseTriggerDT(BaseModel):
    model_config = ConfigDict(extra='forbid')


class CronTriggerDT(BaseTriggerDT):
    """
    The data type representation of apscheduler.triggers.cron.CronTrigger's arguments

    :param int|str year: 4-digit year
    :param int|str month: month (1-12)
    :param int|str day: day of month (1-31)
    :param int|str week: ISO week (1-53)
    :param int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    :param int|str hour: hour (0-23)
    :param int|str minute: minute (0-59)
    :param int|str second: second (0-59)
    :param datetime|str start_date: earliest possible date/time to trigger on (inclusive)
    :param datetime|str end_date: latest possible date/time to trigger on (inclusive)
    :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (defaults
        to scheduler timezone)
    :param int|None jitter: delay the job execution by ``jitter`` seconds at most
    """
    year: int|str = None
    month: int|str = None
    day: int|str = None
    week: int|str = None
    day_of_week: int|str = None
    hour: int|str = None
    minute: int|str = None
    second: int|str = None
    start_date: str = None
    end_date: str = None
    timezone: str = None
    jitter: int = None


class IntervalTriggerDT(BaseTriggerDT):
    """
    The data type representation of apscheduler.triggers.interval.IntervalTrigger's arguments

    :param int weeks: number of weeks to wait
    :param int days: number of days to wait
    :param int hours: number of hours to wait
    :param int minutes: number of minutes to wait
    :param int seconds: number of seconds to wait
    :param datetime|str start_date: starting point for the interval calculation
    :param datetime|str end_date: latest possible date/time to trigger on
    :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations
    :param int|None jitter: delay the job execution by ``jitter`` seconds at most
    """
    weeks: int = None
    days: int = None
    hours: int = None
    minutes: int = None
    seconds: int = None
    start_date: str = None
    end_date: str = None
    timezone: str = None
    jitter: int = None


class DateTriggerDT(BaseTriggerDT):
    """
    The data type representation of apscheduler.triggers.date.DateTrigger's arguments

    :param datetime|str run_date: the date/time to run the job at
    :param datetime.tzinfo|str timezone: time zone for ``run_date`` if it doesn't have one already
    """
    run_date: str = None
    timezone: str = None
