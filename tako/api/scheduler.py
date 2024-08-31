from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import autoreload

from .. import settings
from ..lib.jobstores import DjangoJobStore
from ..lib.script import script_runner
from ..models import DjangoJobExecution
from ..utils import util


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


background_scheduler = None


def init_scheduler():
    global background_scheduler
    if not background_scheduler:
        background_scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler = background_scheduler

    # setup the executor
    scheduler.add_executor(ThreadPoolExecutor(4))

    # if we use the process pool executor:
    # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    # ProcessPoolExecutor(4, dict(
    #     # use 'fork' instead of 'spawn' to avoid the "apps aren't loaded yet" django error
    #     # https://stackoverflow.com/questions/46908035/apps-arent-loaded-yet-exception-occurs-when-using-multi-processing-in-django
    #     # https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    #     mp_context=multiprocessing.get_context('fork'),
    # ))

    # setup the job store
    scheduler.add_jobstore(DjangoJobStore(), "default")

    add_default_jobs(scheduler)

    return scheduler


def start_scheduler(scheduler):
    print("*Starting scheduler...")
    scheduler.start()
    print("*Scheduler started")

    def stop_scheduler(**kwargs):
        print("*Stopping scheduler...")
        scheduler.shutdown()
        print("*Scheduler shut down successfully!")

    if settings.DEBUG:
        autoreload.file_changed.connect(stop_scheduler)

    return stop_scheduler


def add_default_jobs(scheduler):
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
          day_of_week="mon", hour="00", minute="00"
        ),  # Midnight on Monday, before start of the next work week.
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )

    # for testing
    scheduler.add_job(
        test_job,
        trigger=CronTrigger(minute="*/1"),  # Every 10 seconds
        id="test_job",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        test_script_job,
        trigger=CronTrigger(minute="*/10"),  # Every 10 seconds
        id="hello.py",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )


def test_job():
    print('hello')
    import time
    time.sleep(3)
    print('world')

def test_script_job():
    return script_runner('hello.py')
