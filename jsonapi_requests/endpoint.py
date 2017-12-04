import collections
import json

from pydash import py_

from jsonapi_requests.filter import FilterEncoder


class AbstractRequestEndpoint(object):
    def __init__(self, path, requests, *args, **kwargs):
        self.path = path
        self._requests = requests

        self._args = args
        self._include = []
        self._fields = collections.defaultdict(list)
        self._request_arguments = kwargs

    def include(self, to_include):
        self._include.append(to_include)
        return self

    def fields(self, table, field_name):
        if isinstance(field_name, list):
            self._fields[table] += field_name
        elif isinstance(field_name, str):
            self._fields[table].append(field_name)
        else:
            raise Exception('only list and str is allowed as field_name')

        return self

    @property
    def _request_params(self):
        fields = py_(self._fields) \
            .map_keys(lambda _, k: 'fields[' + k + ']') \
            .map_values(lambda v: ','.join(v)) \
            .value()
        include = ','.join(self._include) or None

        return py_.merge(dict(), {'include': include}, fields)

    @property
    def request_params(self):
        return py_(dict()).merge(self._request_params, self._request_arguments) \
            .omit_by(lambda v: v is None) \
            .value()

    @property
    def endpoint(self):
        endpoint_ = '/'.join([self.path] + py_.map(self._args, str))

        if endpoint_[0] == '/':
            return endpoint_[1:]

        return endpoint_

    def get(self, **kwargs):
        return self._requests.get(
            self.endpoint,
            params=self.request_params,
            **kwargs
        )


class SingleRequestEndpoint(AbstractRequestEndpoint):
    def delete(self, **kwargs):
        return self._requests.delete(self.endpoint, **kwargs)

    def put(self, **kwargs):
        return self._requests.put(self.endpoint, **kwargs)

    def patch(self, **kwargs):
        return self._requests.patch(self.endpoint, **kwargs)


class ListRequestEndpoint(AbstractRequestEndpoint):
    def __init__(self, *args, **kwargs):
        self._filters = kwargs.pop('filters', None)

        super(ListRequestEndpoint, self).__init__(*args, **kwargs)

        self._sort = []
        self._page = {}

    def page_limit(self, value):
        self._page['size'] = value
        return self

    def page_number(self, value):
        self._page['number'] = value
        return self

    def sort(self, field, desc=False):
        self._sort.append(field if not desc else '-' + field)
        return self

    @property
    def _request_params(self):
        return py_.merge(
            dict(),
            super(ListRequestEndpoint, self)._request_params,
            {
                'sort': ','.join(self._sort) or None,
                'page[number]': py_.get(self._page, 'number'),
                'page[size]': py_.get(self._page, 'size'),
                'filter':
                    json.dumps(self._filters, cls=FilterEncoder)
                    if self._filters else None,
            },
        )

    def post(self, **kwargs):
        return self._requests.post(self.endpoint, **kwargs)
