# jsonapi-requests

Flask-REST-JSONAPI client implementation.
* JSON API specification: http://jsonapi.org/
* Flask-REST-JSONAPI: http://flask-rest-jsonapi.readthedocs.io/en/latest/

## Usage example

    In [1]: import jsonapi_requests

    In [2]: api = jsonapi_requests.Api.config({
       ...:     'API_ROOT': 'https://localhost/api/2.0',
       ...:     'AUTH': ('basic_auth_login', 'basic_auth_password'),
       ...:     'VALIDATE_SSL': False,
       ...:     'TIMEOUT': 1,
       ...: })

    In [3]: filters = [jsonapi_requests.Filter('name', 'eq', '162 Sushi')]

    In [4]: endpoint = api.endpoint('networks/cd9c124a-acc3-4e20-8c02-3a37d460df22/available-profiles', single=False, filters=filters)

    In [5]: response = endpoint.page_limit(10).page_number(1).get() 

    In [6]: for profile in  response.payload['data']:
       ...:     print(profile['attributes']['name'])
       ...:
    Out[7]: 162 Sushi

    In [8]: endpoint = api.endpoint('clients', 1, single=True)

    In [9]: response = endpoint.get()

    In [10]: response.payload['data']['attributes']['name']
    Out[11]: client with id 1

    In [12]: endpoint = api.endpoint('cookies')

    In [13]: endpoint.post(object=jsonapi_requests.JsonApiObject(
        attributes={'uuid': '09d3a4fff8d64335a1ee9f1d9d054161', 'domain': 'some.domain.pl'},
        type='cookies'))
    Out[14]: <ApiResponse({'data': {'id': '81', 'attributes': {'uuid': '09d3a4fff8d64335a1ee9f1d9d054161', 'domain': 'some.domain.pl'}, 'type': 'cookies'}})>
