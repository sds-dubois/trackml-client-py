import json
from urllib3 import connection_from_url
from urllib import urlencode


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
    """
    Client for TrackML: https://github.com/sds-dubois/trackML
    """

    def __init__(self, model_id=None, base_url="http://localhost:3000/", cache_size=20):
        """
        Initialize the client.
        If :model_id: is passed, this will be used as the default value when logging experiments.
        :base_url: is the address of the server hosting the TrackML app.
        """
        self.client = Client(base_url)
        self.cache = []
        self.cache_size = cache_size
        self.assert_success = True
        self.logging_params = None
        if model_id is not None:
            self.set_model(model_id)

    def _post_and_assert(self, path, params):
        """
        Post request with parameters :params: to the API path :path:.
        Asserts the request is successful if `self.assert_success == True`.
        Returns the id in the response.
        """
        response = self.client.post(path, **params)
        if self.assert_success:
            assert response["success"]
        return int(response.get("id", 0))

    def get_base_url(self):
        """
        Returns the base url used by the API client
        """
        return self.client.base_url
    
    def new_model(self, name, project_id, description=None):
        """
        Create a model named :name: for project with id :project_id:.
        Can add a optional :description:.
        This returns the id of the model created.
        """
        p = { "model[name]": name, "model[project_id]": project_id, "model[comment]": description }
        response = self._post_and_assert("api/create_model", p)
        self.logging_params = None
        return response

    def new_project(self, name):
        """
        Create a project named :name:.
        This returns the id of the project created.
        """
        p = { "project[name]": name }
        response = self._post_and_assert("api/create_project", p)
        self.logging_params = None
        return response

    def set_model(self, model_id):
        """
        Set a default value for the :model_id:
        """
        self.logging_params = {"experiment[model_id]": model_id}

    def reset_model(self):
        """
        Reset the :model_id: default value
        """
        self.logging_params = None

    def log(self, parameters, scores, model_id=None):
        """
        Log this experiment to the server.
        If :model_id: is None, this will use the default value set 
        at initializeation or with set_model_id.
        """
        p = {
            "experiment[model_id]": model_id or self.logging_params.get("experiment[model_id]"),
            "experiment[parameters]": parameters,
            "experiment[scores]": scores,
        }
        return self._post_and_assert("api/create_experiment", p)

    def deferred_log(self, parameters, scores, model_id=None):
        """
        Store exeperiment in cache.
        If cache is full, this will log the current cache to the server.
        """
        self.cache.append({
            "model_id": model_id or self.logging_params.get("experiment[model_id]"),
            "parameters": parameters,
            "scores": scores
        })

        if len(self.cache) >= self.cache_size:
            self.send_cache()


    def send_cache(self):
        """
        Log all experiments in the cache to the server.
        """
        if len(self.cache) == 0:
            return True
        else:
            response = self._post_and_assert("api/create_experiments", {"experiments": self.cache})
            self.cache = []
            return response
