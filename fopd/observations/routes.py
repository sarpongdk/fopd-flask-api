from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Student, Teacher, Experiment

import uuid, datetime

observations = Blueprint('observations', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200


### Observations

def get_all_observations_by_experiment(experiment_id):
    """get all observations made for a specific experiment"""
    pass

def get_observation_by_id(observation_id):
    """get all observations by id"""
    pass

def delete_observation(observation_id):
    """delete an observation"""
    pass

def create_observation():
    """create new observation"""
    pass

def update_observation(observation_id):
    """update observation"""
    pass