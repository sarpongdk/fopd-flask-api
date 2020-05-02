from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Student, Teacher, Experiment, Observation

import uuid, datetime

observations = Blueprint('observations', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200


### Observations
@observations.route('/api/observation/experiment/<experiment_id>', methods = ['GET'])
def get_all_observations_by_experiment(experiment_id):
    """get all observations made for a specific experiment"""
    experiment = Experiment.query.filter_by(public_id = experiment_id).first()
    if not experiment:
        return jsonify({
            'status': 'fail',
            'message': f'Experiment id `{experiment_id}` does not exist'
        }), ERROR_CODE

    observations = []
    for observation in experiment.observations:

        collaborators = []
        for student in observation.student_collaborators:
            collaborators.append({
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            })

        observations.append({
            'title': observation.title,
            'id': observation.public_id,
            'description': observation.description,
            'units': observation.units,
            'updated': observation.updated,
            'type': observation.type,
            'collaborators': collaborators,
        })

    return jsonify({
        'status': 'success',
        'observations': observations
    }), SUCCESS_CODE
    pass

@observations.route('/api/observation/<observation_id>', methods = ['GET'])
def get_observation_by_id(observation_id):
    """get all observations by id"""
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE

    collaborators = []
    for student in observation.student_collaborators:
        collaborators.append({
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username,
            'id': student.public_id
        })

    return jsonify({
        'status': 'success',
        'observation': {
            'title': observation.title,
            'id': observation.public_id,
            'description': observation.description,
            'units': observation.units,
            'updated': observation.updated,
            'type': observation.type,
            'collaborators': collaborators,    
        }
    }), SUCCESS_CODE

@observations.route('/api/observation/<observation_id>', methods = ['DELETE'])
def delete_observation(observation_id):
    """delete an observation"""
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE

    try:
        db.session.delete(observation)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Observation id `{observation_id}` has been deleted'
        }), SUCCESS_CODE
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': f'Unable to delete observation id `{observation_id}`'
        }), ERROR_CODE

@observations.route('/api/observation', methods = ['POST'])
def create_observation():
    """create new observation"""
    pass

@observations.route('/api/observation/<observation_id>', methods = ['PUT', 'POST'])
def update_observation(observation_id):
    """update observation"""
    pass