from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Student, Teacher, Experiment, Device

import uuid, datetime

experiments = Blueprint('experiments', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

### Experiment

@experiments.route('/api/experiment/teacher/<teacher_id>', methods = ['GET'])
def get_teacher_experiments(teacher_id):
    """get teacher's experiments list"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE
    
    experiments = []
    for experiment in teacher.experiments:
        students = []

        for student in experiment.students:
            student_output = {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            }

            students.append(student_output)

        output = {
            'title': experiment.title,
            'description': experiment.description,
            'plant': experiment.plant,
            'start_date': str(experiment.start_date),
            'id': experiment.public_id,
            'students': students,
            'num_students': len(students),
            'device': {
                'id': experiment.device.public_id,
                'name': experiment.device.name
            }
        }

        experiments.append(output)

    return jsonify({
        'status': 'success',
        'num_experiments': len(experiments),
        'experiments': experiments
    })

@experiments.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['GET'])
def get_experiment_by_id(teacher_id, experiment_id):
    """get specific experiment belonging to specific teacher"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment = Experiment.query.filter_by(public_id = experiment_id).first()
    if not experiment:
        return jsonify({
            'status': 'fail',
            'message': 'Experiment does not exist'
        }), ERROR_CODE

    if experiment.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permissions to access experiment'
        }), ERROR_CODE

    students = []
    for student in experiment.students:
        student_output = {
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username,
            'id': student.public_id
        }

        students.append(student_output)

    experiment_output = {
        'title': experiment.title,
        'description': experiment.description,
        'plant': experiment.plant,
        'start_date': str(experiment.start_date),
        'id': experiment.public_id,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'id': teacher.public_id,
            'username': teacher.username
        },
        'students': students,
        'device': {
            'id': experiment.device.public_id,
            'name': experiment.device.name
        }
    }

    return jsonify({
        'status': 'success',
        'experiment': experiment_output
    }), SUCCESS_CODE


@experiments.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['DELETE'])
def delete_experiment(teacher_id, experiment_id):
    """delete experiment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment = Experiment.query.filter_by(public_id = experiment_id).first()
    if not experiment:
        return jsonify({
            'status': 'fail',
            'message': 'Experiment does not exist'
        }), ERROR_CODE

    if experiment.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permissions to access experiment'
        }), ERROR_CODE

    try:
        db.session.delete(experiment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Experiment has been deleted'
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to delete experiment'
        }), ERROR_CODE

@experiments.route('/api/experiment/teacher/<teacher_id>', methods = ['POST'])
def create_experiment(teacher_id):
    """create new experiment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment_info = request.json

    if not experiment_info:
        return jsonify({
            'status': 'fail',
            'message': 'No experiment information provided'
        }), ERROR_CODE

    device_id = experiment_info.get('device_id', None)
    if not device_id:
        return jsonify({
            'status': 'fail',
            'message': 'Cannot create experiment without a device'
        }), ERROR_CODE

    device = Device.query.filter_by(public_id = device_id).first()
    if not device:
        return jsonify({
            'status': 'fail',
            'message': f'Device id `{device_id} does not exist`'
        }), ERROR_CODE

    experiment = Experiment(
        title = experiment_info.get('title', 'No title'),
        description = experiment_info.get('description', 'No description'),
        plant = experiment_info['plant'],
        public_id = str(uuid.uuid4()),
        start_date = experiment_info.get('start_date', datetime.date.today())
    )
    experiment.teacher = teacher
    experiment.device = device

    student_ids = experiment_info.get('student_ids', [])

    experiment.students = []
    student_output = []
    if student_ids:
        for student_id in student_ids:
            student = Student.query.filter_by(public_id = student_id).first()

            if student:
                student.experiments.append(experiment)
                # experiment.students.append(student)

                output = {
                    'fname': student.fname,
                    'lname': student.lname,
                    'username': student.username,
                    'id': student.public_id
                }
                student_output.append(output)

    try:
        db.session.add(experiment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully created experiment',
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'teacher': {
                    'fname': experiment.teacher.fname,
                    'lname': experiment.teacher.lname,
                    'username': experiment.teacher.username,
                    'id': experiment.teacher.public_id
                },
                'students': student_output
            },
            'device': {
                'id': experiment.device.public_id,
                'name': experiment.device.name
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create experiment',
            'error': str(e)
        }), ERROR_CODE

@experiments.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_experiment(teacher_id, experiment_id):
    """update experiment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment = Experiment.query.filter_by(public_id = experiment_id).first()
    if not experiment:
        return jsonify({
            'status': 'fail',
            'message': 'Experiment does not exist'
        }), ERROR_CODE

    experiment_info = request.json

    if not experiment_info:
        return jsonify({
            'status': 'fail',
            'message': f'No experiment information provided to update experiment `{experiment_id}`'
        }), ERROR_CODE

    student_ids = experiment_info.get('student_ids', [])
    
    student_output = []
    for student_id in student_ids:
        student = Student.query.filter_by(public_id = student_id).first()

        if student:
            # student.experiments.append(experiment)
            experiment.students.append(student)

            output = {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            }
            student_output.append(output)

    if experiment_info.get('title', None):
        experiment.title = experiment_info['title']

    if experiment_info.get('plant', None):
        experiment.plant = experiment_info['plant']

    if experiment_info.get('description', None):
        experiment.description = experiment_info['description']

    try:
        db.session.add(experiment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Experiment has been updated',
            'experiment': {
                'title': experiment.title,
                'description': experiment.description,
                'plant': experiment.plant,
                'id': experiment.public_id,
                'students': student_output,
                'teacher': {
                    'fname': teacher.fname,
                    'lname': teacher.lname,
                    'username': teacher.username,
                    'id': teacher.public_id
                }
            },
            'device': {
                'id': experiment.device.public_id,
                'name': experiment.device.name
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update course information'
        }), ERROR_CODE

@experiments.route('/api/experiment/student/<student_id>', methods = ['GET'])
def get_all_student_experiments(student_id):
    """get all student's experiments"""
    student = Student.query.filter_by(public_id = student_id).first()
    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Account id `{student_id}` does not exist'
        }), ERROR_CODE

    experiments_output = []
    for experiment in student.experiments:
        output = {
            'id': experiment.public_id,
            'title': experiment.title,
            'description': experiment.description,
            'plant': experiment.plant,
            'start_date': str(experiment.start_date),
            'teacher': {
                'fname': experiment.teacher.fname,
                'lname': experiment.teacher.lname,
                'username': experiment.teacher.username,
                'id': experiment.teacher.public_id
            },
            'device': {
                'id': experiment.device.public_id,
                'name': experiment.device.name
            }
        }

        experiments_output.append(output)

    return jsonify({
        'status': 'success',
        'num_experiments': len(experiments_output),
        'experiments': experiments_output
    }), SUCCESS_CODE