from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Student, Teacher, Experiment, Observation, ObservationResponse

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

        experiment = observation.experiment
        observations.append({
            'title': observation.title,
            'id': observation.public_id,
            'description': observation.description,
            'units': observation.units,
            'updated': str(observation.updated),
            'type': observation.type,
            'collaborators': collaborators,
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'start_date': str(experiment.start_date)
            }
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

    experiment = observation.experiment
    return jsonify({
        'status': 'success',
        'observation': {
            'title': observation.title,
            'id': observation.public_id,
            'description': observation.description,
            'units': observation.units,
            'updated': str(observation.updated),
            'type': observation.type,
            'collaborators': collaborators,   
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'start_date': str(experiment.start_date)
            } 
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
    observation_info = request.json
    if not observation_info:
        return jsonify({
            'status': 'fail',
            'message': f'No observation information provided'
        }), ERROR_CODE

    experiment_id = observation_info.get('experiment_id', None)
    if not experiment_id:
        return jsonify({
            'status': 'fail',
            'message': f'Cannot create observation without experiment. Provide experiment id'
        }), ERROR_CODE

    student_ids = observation_info.get('student_ids', None)
    if not student_ids:
        return jsonify({
            'status': 'fail',
            'message': f'No student collaborator information provided'
        }), ERROR_CODE  

    experiment = Experiment.query.filter_by(public_id = experiment_id)
    student_collaborators = []

    collaborators_output = []
    for student_id in student_ids:
        student = Student.query.filter_by(public_id = student_id).first()

        if student:
            student_collaborators.append(student)
            collaborators_output.append({
                'id': student.public_id,
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username
            })

    observation = Observation(
        title = observation_info.get('title', 'No title'),
        description = observation_info.get('description', 'No description'),
        type = observation_info['type'],
        units = observation_info['units'],
        updated = datetime.date.today(),
        public_id = str(uuid.uuid4()),
        experiment = experiment,
        student_collaborators = student_collaborators
    )

    try:
        db.session.add(observation)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'title': observation.title,
            'description': observation.description,
            'updated': str(observation.updated),
            'units': observation.units,
            'type': observation.type,
            'id': observation.public_id,
            'student_collaborators': collaborators_output,
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'start_date': str(experiment.start_date)
            }
        }), SUCCESS_CODE

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create observation'
        }), ERROR_CODE

@observations.route('/api/observation/<observation_id>', methods = ['PUT', 'POST'])
def update_observation(observation_id):
    """update observation"""
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE

    observation_info = request.json
    if not observation_info:
        return jsonify({
            'status': 'fail',
            'message': f'No observation information provided'
        }), ERROR_CODE

    title = observation_info.get('title', None)
    description = observation_info.get('description', None)
    updated = observation_info.get('updated', datetime.date.today())
    units = observation_info.get('units', None)
    type = observation_info.get('type', None)
    student_ids = observation_info.get('student_ids', None)

    if title:
        observation.title = title
    
    if description:
        observation.description = description
    
    if updated:
        observation.updated = updated
    
    if units:
        observation.units = units
    
    if type:
        observation.type = type
    
    student_collaborators = []
    if student_ids:
        for student_id in student_ids:
            student = Student.query.filter_by(public_id = student_id)

            if student:
                student_collaborators.append({
                    'id': student.public_id,
                    'fname': student.fname,
                    'lname': student.lname,
                    'username': student.username
                })
                observation.append(student)

    experiment = observation.experiment
    try:
        db.session.add(observation)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'title': observation.title,
            'description': observation.description,
            'updated': str(observation.updated),
            'units': observation.units,
            'type': observation.type,
            'id': observation.public_id,
            'collaborators': student_collaborators,
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'start_date': str(experiment.start_date)
            }
        }), SUCCESS_CODE

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to update observation id `{observation_id}`'
        }), ERROR_CODE

@observations.route('/api/observation/<observation_id>/response', methods = ['POST'])
def add_observation_response(observation_id):
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE


    info = request.json
    if not info:
        return jsonify({
            'status': 'fail',
            'message': f'No observation information provided'
        }), ERROR_CODE

    student_id = info.get('student_id', None)
    if not student_id:
        return jsonify({
            'status': 'fail',
            'message': 'No student id provided'
        }), ERROR_CODE

    student = Student.query.filter_by(public_id = student_id).first()
    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Account id `{student_id}` does not exist'
        }), ERROR_CODE

    response = ObservationResponse(
        response = info.get('response', ''),
        public_id = str(uuid.uuid4()),
        submitted = info.get('submitted', datetime.date.today()),
        editable = True
    )

    response.observation = observation
    response.student = student

    try:
        db.session.add(response)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'response': response.response,
            'submitted': str(response.submitted),
            'editable': response.editable,
            'id': response.public_id,
            'number': response.id,
            'student': {
                'id': student.public_id,
                'username': student.username,
                'fname': student.fname,
                'lname': student.lname
            }
        }), SUCCESS_CODE

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create observation response'
        }), ERROR_CODE

def update_observation_response(observation_id, student_id, response_id):
    pass


@observations.route('/api/observation/<observation_id>/response/<response_id>', methods = ['DELETE'])
def delete_observation_response(observation_id, response_id):
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE

    response = ObservationResponse.query.filter_by(public_id = response_id).first()
    if not response:
        return jsonify({
            'status': 'fail',
            'message': f'Observation response id `{response_id}` does not exist'
        }), ERROR_CODE

    try:
        db.session.delete(response)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Observation response id `{response_id}` has been deleted'
        }), SUCCESS_CODE
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': f'Unable to delete observation response id `{response_id}`'
        }), ERROR_CODE

@observations.route('/api/observation/<observation_id>/response/<response_id>', methods = ['PUT', 'POST'])
def update_observation_response_lock(observation_id, response_id):
    observation = Observation.query.filter_by(public_id = observation_id).first()
    if not observation:
        return jsonify({
            'status': 'fail',
            'message': f'Observation id `{observation_id}` does not exist'
        }), ERROR_CODE

    response = ObservationResponse.query.filter_by(public_id = response_id).first()
    if not response:
        return jsonify({
            'status': 'fail',
            'message': f'Observation response id `{response_id}` does not exist'
        }), ERROR_CODE

    response.editable = False

    student = response.student
    
    try:
        db.session.add(response)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'response': response.response,
            'submitted': str(response.submitted),
            'editable': response.editable,
            'id': response.public_id,
            'number': response.id,
            'student': {
                'id': student.public_id,
                'username': student.username,
                'fname': student.fname,
                'lname': student.lname
            }
        }), SUCCESS_CODE

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to lock observation response id {response_id}'
        }), ERROR_CODE