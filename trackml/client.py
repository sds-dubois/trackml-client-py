import json
from urllib3 import connection_from_url
from urllib import urlencode
from copy import deepcopy


class Client(object):
    """
    A simple JSON API client
    """

    def __init__(self, base_url="http://localhost:3000/", encoding='utf8'):
        self.base_url = base_url
        self.encoding = encoding
        self.connection_pool = connection_from_url(self.base_url)

    def _compose_url(self, path, params=None):
        return self.base_url + path + '?' + urlencode(params)

    def _handle_response(self, response):
        return json.loads(response.data.decode(self.encoding))

    def _request(self, method, path, params=None):
        url = self._compose_url(path, params)
        r = self.connection_pool.urlopen(method.upper(), url)
        return self._handle_response(r)

    def get(self, path, **params):
        return self._request('GET', path, params=params)

    def post(self, path, **params):
        return self._request('POST', path, params=params)


class TrackML(object):

    def __init__(self, logging_params=None, base_url="http://localhost:3000/"):
        self.client = Client(base_url)
        if logging_params is not None:
            self.set_logger(logging_params.get("model_id", None))

    def _post_and_assert(self, path, params):
        response = self.client.post(path, **params)
        assert response["success"]
        return int(response["id"])

    def get_base_url(self):
        return self.client.base_url
    
    def set_logger(self, model_id):
        self.logging_params = {"experiment[model_id]": model_id}

    def reset_logger(self):
        self.logging_params = None

    def new_model(self, name, project_id, description=None):
        p = { "model[name]": name, "model[project_id]": project_id, "model[comment]": description }
        response = self._post_and_assert("api/create_model", p)
        self.logging_params = None
        return response

    def new_project(self, name):
        p = { "project[name]": name }
        response = self._post_and_assert("api/create_project", p)
        self.logging_params = None
        return response

    def log(self, parameters, scores, model_id=None):
        p = {} if self.logging_params is None else deepcopy(self.logging_params)

        if model_id is not None:
            p["experiment[model_id]"] = model_id

        p["experiment[parameters]"] = parameters
        p["experiment[scores]"] = scores

        return self._post_and_assert("api/create_experiment", p)
