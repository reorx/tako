
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


class ParamsError(Exception):
    pass


def get_param(request, key, type_class=None, default=None):
    v = request.GET.getlist(key, [])
    if not v:
        return default
    try:
        v = [type_class(i) if type_class else i for i in v]
    except (TypeError, ValueError) as e:
        raise ParamsError(str(e))
    if len(v) == 1:
        return v[0]
    return v


class APIView(View):
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


def get_executions_params(request):
    params = {}

    job_id = get_param(request, 'job_id', int)
    if job_id is not None:
        params['job_id'] = job_id

    status = get_param(request, 'status')
    if status:
        if isinstance(status, str):
            status = [status]
        params['status'] = status

    request.params = params
    return params


def filter_executions_qs(request, qs):
    params = get_executions_params(request)
    if 'job_id' in params:
        qs = qs.filter(job_id=params['job_id'])
    if 'status' in params:
        qs = qs.filter(status__in=params['status'])
    return qs


def get_page_range(origin_range, num_pages, limit, surround, number, ellipsis='...'):
    if num_pages > limit:
        left = []
        right = []
        surrounded = list(range(max(number - surround, 1), min(number + surround + 1, num_pages)))
        if surrounded[0] <= 1 + surround + 1:
            left = list(range(1, surrounded[0]))
            right = list(range(num_pages - surround, num_pages + 1))
            right.insert(0, ellipsis)
        elif surrounded[0] > 1 + surround + 1 and surrounded[-1] < num_pages - surround - 1:
            left = list(range(1, 1 + surround + 1))
            left.append(ellipsis)
            right = list(range(num_pages - surround, num_pages + 1))
            right.insert(0, ellipsis)
        else:
            left = list(range(1, surround + 1))
            left.append(ellipsis)
            right = list(range(surrounded[-1] + 1, num_pages + 1))

        return left + surrounded + right
    else:
        return origin_range
