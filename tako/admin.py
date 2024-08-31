import json

from apscheduler.util import normalize
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Avg
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .api.scheduler import get_scheduler
from .api.task import create_or_update_task_from_obj, delete_task
from .api.types import CronTriggerDT, DateTriggerDT, IntervalTriggerDT
from .lib.jobstores import DjangoJobStore, DjangoMemoryJobStore
from .models import DjangoJob, DjangoJobExecution, ScriptVersion, Task
from .utils import util


@admin.register(DjangoJob)
class DjangoJobAdmin(admin.ModelAdmin):
    search_fields = ["id"]
    list_display = ["id", "local_run_time", "average_duration"]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        self._django_jobstore = DjangoJobStore()
        self._memory_jobstore = DjangoMemoryJobStore()

        self._job_execution_timeout = getattr(
            settings, "APSCHEDULER_RUN_NOW_TIMEOUT", 15
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        self.avg_duration_qs = (
            DjangoJobExecution.objects.filter(
                job_id__in=qs.values_list("id", flat=True)
            )
            .order_by("job_id")
            .values_list("job")
            .annotate(avg_duration=Avg("duration"))
        )

        return qs

    def local_run_time(self, obj):
        if obj.next_run_time:
            return util.get_local_dt_format(obj.next_run_time)

        return "(paused)"

    def average_duration(self, obj):
        try:
            return self.avg_duration_qs.get(job_id=obj.id)[1]
        except DjangoJobExecution.DoesNotExist:
            return "None"

    average_duration.short_description = _("Average Duration (sec)")

    actions = ["run_selected_jobs"]

    def run_selected_jobs(self, request, queryset):

        for item in queryset:
            django_job, job = self._django_jobstore.lookup_job_v2(item.id)
            # print('run job', job)

            if not django_job:
                msg = _("Could not find job {} in the database! Skipping execution...")
                self.message_user(request, format_html(msg, item.id), messages.WARNING)
                continue

            job.next_run_time = normalize(timezone.now())

            self._django_jobstore.update_job(job)

            get_scheduler().wakeup()

            self.message_user(request, format_html(_("Executed job '{}'!"), django_job.id))

        return None

    run_selected_jobs.short_description = _("Run the selected django jobs")


@admin.register(DjangoJobExecution)
class DjangoJobExecutionAdmin(admin.ModelAdmin):
    status_color_mapping = {
        DjangoJobExecution.SUCCESS: "green",
        DjangoJobExecution.SENT: "blue",
        DjangoJobExecution.MAX_INSTANCES: "orange",
        DjangoJobExecution.MISSED: "orange",
        DjangoJobExecution.ERROR: "red",
    }

    list_display = ["id", "job", "html_status", "local_run_time", "duration_text"]
    list_filter = ["job__id", "run_time", "status"]

    def html_status(self, obj):
        return mark_safe(
            f'<p style="color: {self.status_color_mapping[obj.status]}">{obj.status}</p>'
        )

    def local_run_time(self, obj):
        return util.get_local_dt_format(obj.run_time)

    def duration_text(self, obj):
        return obj.duration or "N/A"

    html_status.short_description = _("Status")
    duration_text.short_description = _("Duration (sec)")


def get_task_form_help_texts():
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    examples = {
        'cron': ('run every 30 seconds', {
            'second': '*/30',
        }),
        'interval': ('run every 1 hour', {
            'hours': 1,
        }),
        'date': ('run on 2024-08-31 20:00:00 in Asia/Shanghai', {
            'run_date': '2024-08-31 20:00:00',
            'timezone': 'Asia/Shanghai',
        }),
    }

    type_lines = []
    params_lines = []
    for trigger_cls in [CronTrigger, IntervalTrigger, DateTrigger]:
        doc_sp = trigger_cls.__doc__.strip().split('\n\n')
        name = trigger_cls.__name__.split('Trigger')[0].lower()

        type_text = doc_sp[0].strip()
        type_lines.append(
            f'<div style="margin-bottom: 4px;"><b>{name}</b>: {type_text}</div>'
        )

        params_text = '\n'.join(i.strip() for i in doc_sp[1].strip().splitlines())
        example_name, example_data = examples[name]
        params_lines.append(
            f'<details style="margin-bottom: 4px;">'
            f'<summary>{name} parameters</summary>'
            '<div style="margin-left: 1em;">'
            f'<pre>{params_text}</pre>'
            f'<div>Example: {example_name}<pre><code>{json.dumps(example_data, indent=2)}</code></pre></div>'
            '</div></details>'
        )

    return {
        'trigger_type': mark_safe(''.join(type_lines)),
        'trigger_value': mark_safe('\n'.join(params_lines)),
        'job': 'Job will be added automatically when the task is saved',
    }


class TaskForm(forms.ModelForm):
    name = forms.CharField(required=False, label='Name', help_text='Unique identifier of the task, if omitted, the filename of the script will be used')

    class Meta:
        # model = Task
        help_texts = get_task_form_help_texts()

    def clean(self):
        name = self.cleaned_data.get('name')
        if not name:
            script = self.cleaned_data['script']
            name = script.filename
            if Task.objects.filter(name=name).exists():
                raise forms.ValidationError('Task with the same name (script filename) already exists')
        self.cleaned_data['name'] = name
        return self.cleaned_data

    def clean_trigger_value(self):
        trigger_type = self.cleaned_data['trigger_type']
        trigger_value = self.cleaned_data['trigger_value']
        if trigger_type and not trigger_value:
            raise forms.ValidationError('trigger_value is required when trigger_type is set')

        try:
            match trigger_type:
                case 'cron':
                    CronTriggerDT.model_validate(trigger_value)
                case 'interval':
                    IntervalTriggerDT.model_validate(trigger_value)
                case 'date':
                    DateTriggerDT.model_validate(trigger_value)
        except Exception as e:
            raise forms.ValidationError(str(e))

        return trigger_value


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskForm

    readonly_fields = ['job']
    list_display = ["name", "job", "script", "trigger_type", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        # data = form.cleaned_data
        # data: {'name': '', 'script': <ScriptVersion: script_1.py - v0>, 'script_args': '', 'trigger_type': 'cron', 'trigger_value': {'minute': '*/5'}}
        # obj: Task<{'id': None, 'name': None, 'job': None, 'script': 1, 'script_args': '', 'trigger_type': 'cron', 'trigger_value': {'minute': '*/5'}}>

        create_or_update_task_from_obj(obj)

    def delete_model(self, request, obj):
        # print('delete_model', obj)
        delete_task(obj)

    def delete_queryset(self, request, queryset):
        with atomic():
            for obj in queryset:
                # print('delete_queryset', obj)
                delete_task(obj)


@admin.register(ScriptVersion)
class ScriptVersionAdmin(admin.ModelAdmin):
    list_display = ["filename", "version", "created_at", "updated_at"]
