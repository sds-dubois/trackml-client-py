# trackML client for Python

*A Python library to manage your machine learning experiments with [trackML](https://github.com/sds-dubois/trackML)*


## Getting started

Be sure to have your [trackML](https://github.com/sds-dubois/trackML) server running. 

Check a full working example [here](examples/simple_example.py). 

In short, you can log an experiment with the following:

```
from trackml import TrackML
logger = TrackML(model_id=1)

hp = {"n_estimators": 20, "max_features": 5}
scores = {"metric1": 0.95, "metric2": 0.78}
logger.log(candidate, scores)
```

By default, this will assume your trackML server is running on `http://localhost:3000` but you can specify another port or domain when initializing the logger:
```
logger = TrackML(base_url="https://www.mydomain.com")
```

## Deferred logging

The `log` method will instantly post the experiment information. If you want to avoid potential slow downs due to the http requests, you can defer the requests to send experiments in batches (whenever the cache is full).

In that case you would call `deferred_log`:
```
# default cache size is 20
# change it at initialization: logger = TrackML(model_id=1, cache_size=50)

candidates = [...]
for candidate in candidates:
    scores = {"metric": model.eval(candidate)}
    logger.deferred_log(candidate, scores) # this will only send a request if cache is full
logger.send_cache()
```

**Important** - be sure to call `logger.send_cache()` to log pending experiments.


## Create projects and models

You can also use this client to create projects or models.

```
logger = TrackML()

project_id = logger.new_project("Awesome Project")
model_id = logger.new_model("Baseline", project_id, description="An optional description")
```

You can finally set a default model ID by calling `logger.set_model(model_id)` of specify it when calling log/deferred_log: `logger.log(candidate, scores, model_id)`.

## Ensure successful logs

By default, the client doesn't check the request was successful. To turn this on, initialize the logger as follows:
```
logger = TrackML(assert_success=True)
```

## License 

[MIT License](LICENSE.md)
