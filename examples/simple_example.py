"""
Simple example inspired by:
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_randomized_search.html
"""

from trackml import TrackML

import numpy as np

from scipy.stats import randint as sp_randint

from sklearn.model_selection import RandomizedSearchCV, ParameterSampler, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_digits

# initialize logger with model id and metric
model_id = 1
logger = TrackML({ "model_id": model_id })

# # or we could create a new model here
# logger = TrackML()
# model_id = logger.new_model(name="Simple Test", project_id=1)
# logger.set_logger(model_id, metric="accuracy")


# get some data
digits = load_digits()
X, y = digits.data, digits.target

n_iter_search = 5
random_state = 0


# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, None],
              "max_features": sp_randint(1, 11),
              "min_samples_split": sp_randint(2, 11),
              "min_samples_leaf": sp_randint(1, 11),
              "criterion": ["gini", "entropy"]}

# sample HP candidates to test
candidates = list(ParameterSampler(param_dist, n_iter_search, random_state))

for candidate in candidates:
    clf = RandomForestClassifier(n_estimators=20, **candidate)
    accuracy = np.mean(cross_val_score(clf, X, y, cv=5))
    precision = np.mean(cross_val_score(clf, X, y, cv=5, scoring="precision_macro"))
    scores = {"accuracy": accuracy, "precision_macro": precision}
    logid = logger.log(candidate, scores) # if model_id already set
    # logid = logger.log(candidate, scores, model_id=1) # otherwise

print("See results at {}/models/{}".format(logger.get_base_url(), model_id))
