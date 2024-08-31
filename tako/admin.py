

from apscheduler.util import normalize
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Avg
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .lib.jobstores import DjangoJobStore, DjangoMemoryJobStore
from .models import DjangoJob, DjangoJobExecution
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
        from .api.scheduler import background_scheduler as scheduler

        for item in queryset:
            django_job, job = self._django_jobstore.lookup_job_v2(item.id)
            # print('run job', job)

            if not django_job:
                msg = _("Could not find job {} in the database! Skipping execution...")
                self.message_user(request, format_html(msg, item.id), messages.WARNING)
                continue

            job.next_run_time = normalize(timezone.now())

            self._django_jobstore.update_job(job)

            scheduler.wakeup()

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
