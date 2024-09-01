
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ..models import DjangoJobExecution


class ParamsError(Exception):
    pass


class ParamsMixin:
    def get_param(self, key, type_class, default=None):
        v = self.request.GET.get(key, '')
        if not v:
            return default
        try:
            return type_class(v)
        except (TypeError, ValueError) as e:
            raise ParamsError(str(e))


class APIView(ParamsMixin, View):
    superuser_required = False
    is_json = True

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if self.superuser_required:
            if not (
                request.user.is_authenticated and request.user.is_superuser
            ):
                return self.json_response(
                    {
                        'success': False,
                        'error': 'superuser required'
                    }, 403
                )

        try:
            self.parse_body()
        except Exception as e:
            return self.json_response(
                {
                    'success': False,
                    'error': f'invalid request json body: {e}'
                }, 400
            )

        return super(APIView, self).dispatch(request, *args, **kwargs)

    def parse_body(self):
        if self.is_json:
            self.json = json.loads(self.request.body)

    @staticmethod
    def json_response(data, status=200, encoder=None, json_dumps_params=None, **kwargs):
        json_dumps_params = json_dumps_params or {}
        json_dumps_params.update({'ensure_ascii': False})

        return JsonResponse(
            data,
            encoder=encoder or DjangoJSONEncoder,
            json_dumps_params=json_dumps_params,
            safe=False,
            status=status,
            **kwargs,
        )



def filter_execution_by_success(qs, is_success):
    if is_success:
        qs = qs.filter(status=DjangoJobExecution.SUCCESS)
    else:
        qs = qs.filter(~Q(status=DjangoJobExecution.SUCCESS))
    return qs


def executions_queryset(self, qs):
    self.qs_args = []

    def append_qs_arg(k, v):
        if v is not None:
            self.qs_args.append((k, v))

    job_id = self.get_param('job_id', int)
    append_qs_arg('job_id', job_id)

    status = self.get_param('status', str)
    append_qs_arg('status', status)

    if job_id:
        qs = qs.filter(task_trigger_id=job_id)
    if status:
        qs = filter_execution_by_success(qs, status == DjangoJobExecution.SUCCESS)

    return qs
