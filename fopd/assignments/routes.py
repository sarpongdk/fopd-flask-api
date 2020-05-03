from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Student, Teacher, Assignment

import uuid, datetime

assignments = Blueprint('assignments', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

### Assignments
@assignments.route('/api/assignment/student/<student_id>', methods = ['GET'])
def get_all_student_assignments(student_id):
    """get all student assignments"""
    student = Student.query.filter_by(public_id = student_id).first()
    if not student:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignments = student.assignments
    assignment_output = []
    for assignment in assignments:


        output = {
            'id': assignment.public_id,
            'title': assignment.title,
            'description': assignment.description,
            'type': assignment.type,
            'due_date': assignment.due_date
        }
    
        assignment_output.append(output)

    return jsonify({
        'status': 'success',
        'length': len(assignment_output),
        'assignments': assignments,
        'student': {
            'fname': student.fname,
            'lname': student.lname,
            'id': student.public_id,
            'username': student.username
        }
    }), SUCCESS_CODE

    pass

@assignments.route('/api/assignment/teacher/<teacher_id>', methods = ['GET'])
def get_all_teacher_assignments(teacher_id):
    """get all teacher assignments"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignments = teacher.assigned_assignments
    assignment_output = []
    for assignment in assignments:

        output = {
            'id': assignment.public_id,
            'title': assignment.title,
            'description': assignment.description,
            'type': assignment.type,
            'due_date': assignment.due_date
        }
    
        assignment_output.append(output)

    return jsonify({
        'status': 'success',
        'length': len(assignment_output),
        'assignments': assignments,
        'student': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'id': teacher.public_id,
            'username': teacher.username
        }
    }), SUCCESS_CODE

@assignments.route('/api/assignment/<assignment_id>', methods = ['GET'])
def get_assignment_by_id(assignment_id):
    """get assignment by id"""
    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': 'Assignmnet does not exist'
        }), ERROR_CODE

    students = []
    for student in assignment.students:
        output = {
            'fname': student.fname,
            'lname': student.lname,
            'id': student.public_id,
            'username': student.username
        }

        students.append(output)

    teacher = {
        'fname': student.fname,
        'lname': student.lname,
        'id': student.public_id,
        'username': student.username
    }

    return jsonify({
        'status': 'success',
        'num_students': len(students),
        'students': students,
        'teacher': teacher,
        'assignment': {
            'id': assignment.public_id,
            'title': assignment.title,
            'description': assignment.description,
            'type': assignment.type,
            'due_date': assignment.due_date
        }
    }), SUCCESS_CODE

@assignments.route('/api/assignment/teacher/<teacher_id>', methods = ['POST'])
def create_assignment(teacher_id):
    """create new assignment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignment_info = request.json
    if not assignment_info:
        return jsonify({
            'status': 'fail',
            'message': 'No assignment information provided'
        }), ERROR_CODE

    assignment = Assignment(
        title = assignment_info['title'],
        description = assignment_info['description'],
        type = assignment_info['type'],
        due_date = assignment_info['due_date'],
        public_id = str(uuid.uuid4())
    )  

    assignment.teacher = teacher
    student_list = []
    student_ids = assignment_info.get('student_ids', [])
    for student_id in student_ids:
        student = Student.query.filter_by(public_id = student_id).first()
        #student.assignments.append(assignment)

        print(student)
        if student:
            assignment.students.append(student)

            student_list.append({
                'fname': student.fname,
                'lname': student.lname,
                'id': student.public_id,
                'username': student.username
            })

    try:
        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'assignment': {
                'id': assignment.public_id,
                'title': assignment.title,
                'description': assignment.description,
                'type': assignment.type,
                'due_date': assignment.due_date
            }, 
            'students': student_list,
            'num_students': len(student_list),
            'teacher': {
                'fname': teacher.fname,
                'lname': teacher.lname,
                'username': teacher.username,
                'id': teacher.public_id
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Assignment not created'
        }), ERROR_CODE



@assignments.route('/api/assignment/<assignment_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_assignment(teacher_id, assignment_id):
    """update assignment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': 'Experiment does not exist'
        }), ERROR_CODE

    if assignment.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher not authorized to update assignment'
        }), ERROR_CODE

    assignment_info = request.json
    if not assignment_info:
        return jsonify({
            'status': 'fail',
            'message': f'No assignment information provided to update assignment `{assignment_id}`'
        }), ERROR_CODE

    title = assignment_info.get('title', None)
    description = assignment_info.get('description', None)
    type= assignment_info.get('type', None)
    due_date = assignment_info.get('due_date', None)

    if title:
        assignment.title = title

    if type:
        assignment.type = type

    if description:
        assignment.description = description

    if due_date:
        assignment.due_date = due_date

    student_list = []
    student_ids = assignment_info.get('student_ids', [])

    for student_id in student_ids:
        student = Student.query.filter_by(public_id = student_id)

        if student:
            assignment.students.append(student)

            student_list.append({
                'fname': student.fname,
                'lname': student.lname,
                'id': student.public_id,
                'username': student.username
            })

    try:
        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'assignment': {
                'id': assignment.public_id,
                'title': assignment.title,
                'description': assignment.description,
                'type': assignment.type,
                'due_date': assignment.due_date
            }, 
            'students': student_list, # + assignment.students,
            'num_students': len(student_list),
            'teacher': {
                'fname': teacher.fname,
                'lname': teacher.lname,
                'username': teacher.username,
                'id': teacher.public_id
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Assignment not created'
        }), ERROR_CODE

@assignments.route('/api/assignment/<assignment_id>/teacher/<teacher_id>', methods = ['DELETE'])
def delete_assignment(teacher_id, assignment_id):
    """delete assignment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignment = Assignment.query.filter_by(public_id = assignment_id).first()
    if not assignment:
        return jsonify({
            'status': 'fail',
            'message': 'Assignment does not exist'
        }), ERROR_CODE

    if assignment.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher not authorized to delete assignment'
        }), ERROR_CODE

    try:
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Assignment has been deleted'
        }), SUCCESS_CODE

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to delete assignment'
        }), ERROR_CODE
