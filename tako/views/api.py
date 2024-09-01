from django.forms.models import model_to_dict

# TODO import new run task function
# from .admin import run_task
from ..helper.db import get_x_by_y
from ..helper.view import APIView


# TODO import models
# from .models import ManagerJob, ManagerJobExecution, ManagerTask, standard_status
# TODO import job_store
# from .myjobs import job_store


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

    def get(self, request):
        qs = executions_get_queryset(self, ManagerJobExecution.objects.all()).order_by('-run_time')
        qs = qs[:self.ts_items_limit]

        # categorize by status
        tsdict = {}
        for i in qs:
            status = standard_status(i.status)
            d = {
                'id': i.id,
                'date': i.run_time.strftime(self.time_format),
                'status': status,
                'status_class': spectre_label_class_func(i.status),
                'trigger_str': i.trigger_str,
                'duration': f'{i.duration}s' if i.duration is not None else '-',
            }
            l = tsdict.setdefault(status, [])
            l.append(d)

        data = []
        for k, v in tsdict.items():
            v.reverse()
            data.append({
                'name': k,
                'data': v,
            })
        return JsonResponse(data, safe=False)
