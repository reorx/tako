from django.db import models
from django.forms import model_to_dict

from ..utils.enum import KV, SimpleEnum
from .job import DjangoJob


class TriggerType(SimpleEnum):
    cron = KV
    interval = KV
    date = KV


class Task(models.Model):
    """
    | tako  |   django_apscheduler              |
    | Task -|-> DjangoJob -> DjangoJobExecution |
    """
    # name is the id of ScriptTask, which is also used to generate the id of DjangoJob
    name = models.CharField(max_length=64, unique=True)
    job = models.OneToOneField(DjangoJob, null=True, on_delete=models.CASCADE)
    # will be processed by shlex.split(script_args) before passing to subprocess.Popen
    script = models.ForeignKey('ScriptVersion', on_delete=models.DO_NOTHING)
    script_args = models.TextField(null=True, blank=True)

    # trigger
    trigger_type = models.CharField(max_length=16, null=True, blank=True, choices=list(TriggerType.items()))
    trigger_value = models.JSONField(null=True, blank=True)

    # time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tako_task'

    def __str__(self):
        return f'Task<{model_to_dict(self)}>'


class ScriptVersion(models.Model):
    filename = models.CharField(max_length=64)
    version = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.filename} - v{self.version}'

    class Meta:
        db_table = 'tako_script_version'
