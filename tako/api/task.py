

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.db.models import Max, Min
from django.db.transaction import atomic

from ..lib.script import script_dir, script_runner
from ..log import lg
from ..models import Task
from ..models.task import ScriptVersion
from .scheduler import get_scheduler


default_trigger = DateTrigger(run_date='9999-01-01')


def create_task_job(task: Task) -> Job:
    task_name = task.name
    script: ScriptVersion = task.script
    script_args = task.script_args
    trigger_type = task.trigger_type
    trigger_value = task.trigger_value

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
        name=job_id,
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
        job_id = create_task_job(obj)

        obj.job_id = job_id

        obj.save()


# NOTE no need to load task jobs to scheduler as jobstores has handled it automatically
# def load_task_jobs_to_scheduler():
#     for task in Task.objects.all():
#         create_task_job(task)


def create_or_update_script_from_obj(obj: ScriptVersion):
    max_version = None
    qs = ScriptVersion.objects.filter(filename=obj.filename).order_by('-version')
    if qs.exists():
        max_version = qs[0].version

    # script should only be written when it's a new script or the latest version
    should_write_script = False
    if obj.version is None:
        should_write_script = True
        obj.version = max_version + 1 if max_version is not None else 0
    else:
        if obj.version == max_version:
            should_write_script = True

    with atomic():
        if should_write_script:
            write_script(obj.filename, obj.content)
        obj.save()


def write_script(filename, content):
    script_path = script_dir / filename

    with open(script_path, 'w') as f:
        f.write(content)

    lg.info(f'Script written: {script_path}')


def get_latest_scripts() -> list[dict]:
    """get a list of dict with filename, version, created_at, updated_at. sorted by updated_at desc"""
    # NOTE use .values / .values_list at first to group by the field
    # NOTE order_by cannot be used here, as it will mess up the group by
    qs = ScriptVersion.objects.values('filename').annotate(version=Max('version'), created_at=Min('created_at'), updated_at=Max('updated_at'))
    return sorted(qs, key=lambda x: x['updated_at'], reverse=True)
