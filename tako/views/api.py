from django.forms.models import model_to_dict
from django.http import HttpResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from ..api.task import create_or_update_task_from_obj, delete_task, trigger_dt_map
# TODO import new run task function
# from .admin import run_task
from ..helper.db import get_x_by_y
# TODO import models
# from .models import ManagerJob, ManagerJobExecution, ManagerTask, standard_status
# TODO import job_store
# from .myjobs import job_store
from ..lib.jinja2 import get_spectre_label_class
from ..models.job import DjangoJobExecution
from ..models.task import Script, Task, TriggerType
from .base import APIView, filter_executions_qs, handle_exception, json_response, validate_params


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
        qs = filter_executions_qs(
            request,
            DjangoJobExecution.objects.select_related('job').defer('job__job_state').all()
        )[:self.ts_items_limit]

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



class TasksEditParams(BaseModel):
    id: int = None
    name: str
    script_id: int
    script_args: str = ''
    trigger_type: str = Field()
    trigger_value: dict

    @field_validator('trigger_type')
    def validate_trigger_type(cls, value):
        assert value in TriggerType.values(), f'trigger_type must be one of {TriggerType.values()}'
        return value

    @field_validator('trigger_value')
    def validate_trigger_value(cls, value):
        assert value, 'trigger_value must not be empty'
        return value

    @model_validator(mode='after')
    def validate_obj(self):
        type_cls = trigger_dt_map[self.trigger_type]
        type_cls.model_validate(self.trigger_value)
        return self


@validate_params(TasksEditParams, 'POST')
@handle_exception(Exception)
def tasks_create_view(request):
    params: TasksEditParams = request.params
    script = Script.objects.get(id=params.script_id)
    task = Task(
        name='',
        script=script,
        script_args=params.script_args,
        trigger_type=params.trigger_type,
        trigger_value=params.trigger_value,
    )
    create_or_update_task_from_obj(task)

    return json_response({
        'data': {
            'id': task.id,
        },
    })


@validate_params(TasksEditParams, 'POST')
@handle_exception(Exception)
def tasks_update_view(request):
    params: TasksEditParams = request.params
    task = Task.objects.get(id=params.id)

    task.name = params.name
    task.script = Script.objects.get(id=params.script_id)
    task.script_args = params.script_args
    task.trigger_type = params.trigger_type
    task.trigger_value = params.trigger_value

    create_or_update_task_from_obj(task)

    return json_response({
        'data': {
            'id': task.id,
        },
    })


class TasksDeleteParams(BaseModel):
    id: int


@validate_params(TasksDeleteParams, 'POST')
@handle_exception(Exception)
def tasks_delete_view(request):
    params: TasksDeleteParams = request.params
    task = Task.objects.get(id=params.id)
    delete_task(task)

    return HttpResponse(status=204)
