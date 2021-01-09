from django.http import QueryDict
from django.utils.deprecation import MiddlewareMixin


class HttpPostTunnelingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            http_method = request.META['REQUEST_METHOD']

            if http_method.lower() == 'put':
                request.method = 'PUT'
                request.META['REQUEST_METHOD'] = 'PUT'
                request.PUT = QueryDict(request.body)

            elif http_method.lower() == 'patch':
                request.method = 'PATCH'
                request.META['REQUEST_METHOD'] = 'PATCH'
                request.PATCH = QueryDict(request.body)

            elif http_method.lower() == 'delete':
                request.method = 'DELETE'
                request.META['REQUEST_METHOD'] = 'DELETE'
                request.DELETE = QueryDict(request.body)

        except Exception as e:
            pass

        return None
