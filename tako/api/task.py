
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.db.transaction import atomic

from ..lib.script import script_runner
from ..log import lg
from ..models import Task
from ..models.task import ScriptVersion
from .scheduler import get_scheduler


default_trigger = DateTrigger(run_date='9999-01-01')


def create_task_job(task_name, script: ScriptVersion, script_args: str|None, trigger_type, trigger_value) -> Job:
    job_id = f'task:{task_name}'

    trigger = None
    trigger_cls = None
    match trigger_type:
        case 'cron':
            trigger_cls = CronTrigger
        case 'interval':
            trigger_cls = IntervalTrigger
        case 'date':
            trigger_cls = DateTrigger

    if trigger_cls:
        trigger = trigger_cls(**trigger_value)

    if not trigger:
        trigger = default_trigger

    get_scheduler().add_job(
        script_runner,
        args=[script.filename, script_args],
        id=job_id,
        trigger=trigger,
        max_instances=1,
        replace_existing=True,
    )

    return job_id


def delete_task(obj: Task):
    lg.info(f'Deleting task: {obj}')
    with atomic():
        if obj.job_id:
            get_scheduler().remove_job(obj.job_id)
        obj.delete()


def create_or_update_task_from_obj(obj: Task):
    with atomic():
        job_id = create_task_job(obj.name, obj.script, obj.script_args, obj.trigger_type, obj.trigger_value)

        obj.job_id = job_id

        obj.save()
