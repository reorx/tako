from django.forms.models import model_to_dict

# TODO import new run task function
# from .admin import run_task
from ..helper.db import get_x_by_y
from ..models.job import DjangoJobExecution
# TODO import models
# from .models import ManagerJob, ManagerJobExecution, ManagerTask, standard_status
# TODO import job_store
# from .myjobs import job_store
from ..templatetags.tako_filters import get_spectre_label_class
from .base import APIView, executions_queryset


class TaskExecuteView(APIView):
    superuser_required = True

    def post(self, request):
        task_id = self.json.get("task_id")
        task_delay = self.json.get("task_delay", 10)
        if not task_id:
            return self.json_response({'success': False, 'error': 'missing task_id'}, status=400)
        task = get_x_by_y(ManagerTask, 'id', task_id)
        trigger = run_task(task, seconds=task_delay)
        return self.json_response({'success': True, 'data': {
            'task': model_to_dict(task),
            'trigger': model_to_dict(trigger),
        }})



class JobCancelView(APIView):
    superuser_required = True

    def post(self, request):
        job_id = self.json.get("job_id")
        if not job_id:
            return self.json_response({'success': False, 'error': 'missing job_id'}, status=400)
        job = get_x_by_y(ManagerJob, 'id', job_id)
        try:
            job_store.remove_job(job.name)
            return self.json_response({'success': True})
        except Exception as e:
            return self.json_response({'success': False, 'error': str(e)}, status=500)


class ExecutionsTSDataView(APIView):
    ts_items_limit = 1000
    time_format = '%Y-%m-%dT%H:%M:%S%z'
    is_json = False

    def get(self, request):
        qs = executions_queryset(self, DjangoJobExecution.objects.select_related('job').defer('job__job_state').all()).order_by('-run_time')
        qs = qs[:self.ts_items_limit]

        # categorize by status
        tsdict = {}
        for i in qs:
            d = {
                'id': i.id,
                'date': i.run_time.strftime(self.time_format),
                'status': i.status,
                'status_class': get_spectre_label_class(i.status),
                'job_id': i.job.id,
                'duration': f'{i.duration}s' if i.duration is not None else '-',
            }
            l = tsdict.setdefault(i.status, [])
            l.append(d)

        data = []
        for k, v in tsdict.items():
            v.reverse()
            data.append({
                'name': k,
                'data': v,
            })
        return self.json_response(data)
