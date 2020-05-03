from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Student, Teacher, Assignment, AssignmentResponse

import uuid, datetime

assignment_responses = Blueprint('assignment_responses', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200


### Assignment Responses
@assignment_responses.route('/api/assignment/<assignment_id>/response', methods = ['GET'])
def get_all_responses_by_assignment(assignment_id):
    """get assignment responses from assignment id"""
    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': 'Experiment does not exist'
        }), ERROR_CODE

    output = []
    for response in assignment.responses:  
        output.append({
            'id': response.public_id,
            'submitted': response.submitted,
            'comments': response.comments or '',
            'student': {
                'fname': response.student.fname,
                'lname': response.student.lname,
                'username': response.student.username,
                'public_id': response.student.public_id,
            },
            'assignment': {
                'id': assignment.public_id,
                'title': assignment.title,
                'description': assignment.description,
                'type': assignment.type
            },
            'teacher': {
                'fname': assignment.teacher.fname,
                'lname': assignment.teacher.lname,
                'username': assignment.teacher.username,
                'public_id': assignment.teacher.public_id,
            }
        })
    
    return jsonify({
        'status': 'success',
        'assignment_response': output
    }), SUCCESS_CODE


@assignment_responses.route('/api/assignment/<assignment_id>/response/student/<student_id>', methods = ['GET'])
def get_student_assignment_responses_by_assignment_id(student_id, assignment_id):
    """get student's assigment response"""
    student = Student.query.filter_by(public_id = student_id).first()
    if not student:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': f'Assignment id `{assignment_id}` does not exist'
        }), ERROR_CODE

    assignment_response = AssignmentResponse.query.filter_by(assignment_id = assignment_id, student_id = student_id).first()
    if not assignment_response:
        return jsonify({
            'status': 'fail',
            'message': f'Assignment response for assignment with id `{assignment_id}` does not exist'
        }), ERROR_CODE

    response_output = {
        'id': assignment_response.public_id,
        'submitted': assignment_response.submitted,
        'response': assignment_response.response,
        'comments': assignment_response.comments,
        'assignment': {
            'id': assignment.public_id,
            'title': assignment.title,
            'description': assignment.description,
            'type': assignment.type,
            'due_date': assignment.due_date
        },
        'student': {
            'id': student.public_id,
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username
        }
    }

    return jsonify({
        'status': 'success',
        'assignment_response': response_output
    }), SUCCESS_CODE

@assignment_responses.route('/api/assignment/<assignment_id>/response/<assignment_response_id>/student/<student_id>', methods = ['PUT', 'POST'])
def update_student_response(assignment_id, student_id, assignment_response_id):
    """update student assignment response"""
    assignment_response = AssignmentResponse.query.filter_by(assignment_id = assignment_id, public_id = assignment_response_id, student_id = student_id).first()
    if not assignment_response:
        return jsonify({
            'status': 'fail',
            'assignment_response': f'Assignment response id `{assignment_response_id}` does not exist'
        }), ERROR_CODE

    assignment_info = request.json
    if not assignment_info:
        return jsonify({
            'status': 'fail',
            'message': f'No data passed to update assignment response id `{assignment_response_id}`'
        }), ERROR_CODE

    new_response = assignment_info.get('response', None)
    if new_response:
        assignment_response.response = assignment_info.get('response', '')
        assignment_response.submitted = datetime.datetime.utcnow()

    new_comments = assignment_info.get('comments', '')
    if new_comments:
        assignment_response.comments = assignment_info.get('comments', '')

    try:
        db.session.add(assignment_response)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'assignment_response': {
                'response': assignment_response.response,
                'comments': assignment_response.comments,
                'submitted': assignment_response.submitted
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to update assignment response id `{assignment_response.public_id}`'
        }), ERROR_CODE

@assignment_responses.route('/api/assignment/<assignment_id>/response/<assignment_response_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def add_comment_to_assignment_response(teacher_id, assignment_id, assignment_response_id):
    """add comments to assignment response"""
    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': f'Assignment id `{assignment_id}` does not exist'
        }), ERROR_CODE

    assignment_response = AssignmentResponse.query.filter_by(public_id = assignment_response_id).first()
    if not assignment_response:
        return jsonify({
            'status': 'fail',
            'message': f'Assignment response id `{assignment_response_id}` does not exist'
        }), ERROR_CODE

    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account id `{teacher_id}` does not exist'
        }), ERROR_CODE

    comments = request.json.get('comments', None)
    if not comments:
        return jsonify({
            'status': 'fail',
            'message': f'Comments not provided for assignment response `{assignment_response_id}`'
        }), ERROR_CODE

    assignment_response.comments = comments

    try:
        db.session.add(assignment_response)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'assignment_response': {
                'id': assignment_response.public_id,
                'response': assignment_response.response,
                'comments': assignment_response.comments,
                'submitted': assignment_response.submitted,
                'student': {
                    'id': assignment_response.student.public_id,
                    'fname': assignment_response.student.fname,
                    'lname': assignment_response.student.lname,
                    'username': assignment_response.student.username
                }
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to add comments to assignment response `{assignment_response_id}`'
        }), ERROR_CODE

    pass

