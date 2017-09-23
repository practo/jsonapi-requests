try:
    from urllib import parse
except ImportError:
    import urlparse as parse
import json

import requests
import tenacity

from jsonapi_requests.utils import dict_merge


class ApiRequestFactory(object):
    def __init__(self, config):
        self.config = config

    def get(self, api_path, **kwargs):
        return self.request(api_path, 'GET', **kwargs)

    def post(self, api_path, **kwargs):
        return self.request(api_path, 'POST', **kwargs)

    def delete(self, api_path, **kwargs):
        return self.request(api_path, 'DELETE', **kwargs)

    def put(self, api_path, **kwargs):
        return self.request(api_path, 'PUT', **kwargs)

    def patch(self, api_path, **kwargs):
        return self.request(api_path, 'PATCH', **kwargs)

    def request(self, api_path, method, object=None, **kwargs):
        url = self._build_absolute_url(api_path)

        if object is not None:
            assert 'json' not in kwargs
            kwargs['json'] = {'data': object.as_data()}

        return self.retrying.call(self._request, url, method, **kwargs)

    @property
    def retrying(self):
        retry_condition = (
            tenacity.retry_if_exception_type(ApiConnectionError)
            | tenacity.retry_if_exception_type(ApiInternalServerError)
        )
        return tenacity.Retrying(
            reraise=True,
            retry=retry_condition,
            stop=tenacity.stop_after_attempt(self.config.RETRIES)
        )

    def _build_absolute_url(self, api_path):
        url = parse.urljoin(self.config.API_ROOT, api_path)
        if self.config.APPEND_SLASH and not url.endswith('/'):
            url += '/'
        return url

    def _request(self, absolute_url, method, **kwargs):
        options = self.default_options
        dict_merge(options, self.configured_options)
        dict_merge(options, kwargs)
        try:
            response = requests.request(method, absolute_url, **options)
        except (requests.ConnectionError, requests.Timeout):
            raise ApiConnectionError
        else:
            return self._parse_response(response)

    @property
    def default_options(self):
        return {
            'headers': {
                'Content-Type': 'application/vnd.api+json',
                'Accept': 'application/vnd.api+json',
            }
        }

    @property
    def configured_options(self):
        options = {'verify': self.config.VALIDATE_SSL}
        if self.config.AUTH:
            options['auth'] = self.config.AUTH
        if self.config.TIMEOUT:
            options['timeout'] = self.config.TIMEOUT
        return options

    def _parse_response(self, response):
        if response.status_code >= 500:
            raise ApiInternalServerError(response.status_code, response.content)
        elif response.status_code == 204:
            return ApiResponse(response.status_code, {})
        elif 400 <= response.status_code < 500:
            raise ApiClientError(response.status_code, response.content)
        try:
            payload = response.json()
        except ValueError:
            raise ApiInvalidResponseError(response.status_code, response.content)
        else:
            return ApiResponse(response.status_code, payload)


class ApiResponse(object):
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def get_data(self, schema):
        return schema.loads(json.dumps(self.payload)).data

    def __repr__(self):
        return '<ApiResponse({})>'.format(self.payload)


class ApiRequestError(Exception):
    pass


class ApiResponseError(ApiRequestError):
    pass


class ApiInvalidResponseError(ApiRequestError):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


class ApiInternalServerError(ApiInvalidResponseError):
    pass


class ApiClientError(ApiInvalidResponseError):
    pass


class ApiConnectionError(ApiRequestError):
    pass
