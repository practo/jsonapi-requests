from jsonapi_requests import configuration
from jsonapi_requests import request_factory
from jsonapi_requests.endpoint import ListRequestEndpoint
from jsonapi_requests.endpoint import SingleRequestEndpoint
from jsonapi_requests.utils import dict_merge


class Api(object):
    @classmethod
    def config(cls, dict_or_config=None, **kwargs):
        config_dict = {}
        if isinstance(dict_or_config, dict):
            dict_merge(config_dict, dict_or_config)
        else:
            for setting in dir(dict_or_config):
                if setting.isupper():
                    config_dict[setting] = getattr(dict_or_config, setting)
        dict_merge(config_dict, kwargs)
        return cls(configuration.Factory(config_dict).create())

    def __init__(self, config):
        self.requests = request_factory.ApiRequestFactory(config)

    def endpoint(self, path, *args, **kwargs):
        single = kwargs.pop('single', False)

        if single:
            return SingleRequestEndpoint(path, self.requests, *args, **kwargs)
        else:
            return ListRequestEndpoint(path, self.requests, *args, **kwargs)
