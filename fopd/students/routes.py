from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Student, Teacher

import uuid, datetime

students = Blueprint('students', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

### Student

@students.route('/api/student/<student_id>', methods = ['DELETE'])
def delete_student_account(student_id):
    """delete student account by id"""
    student = Student.query.filter_by(public_id = student_id).first()

    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Account id: `{student_id}` has been deleted'
        }), SUCCESS_CODE
    else:
        return jsonify({
            'status': 'fail',
            'message': f'Account id: {student_id} does not exist'
        }), ERROR_CODE

@students.route('/api/student/teacher/<teacher_id>', methods = ['GET'])
def get_all_students_by_teacher(teacher_id):
    """get all students with teacher_id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account id `{teacher_id} `does not exist'
        }), ERROR_CODE
    
    # format output
    output = []
    for student in teacher.students:
        student_output = {
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username,
            'public_id': student.public_id
        }
        output.append(student_output)
    
    return jsonify({
        'status': 'success',
        'length': len(output),
        'students': output,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'username': teacher.username,
            'public_id': teacher.public_id
        }
    }), SUCCESS_CODE


@students.route('/api/student/<student_id>', methods = ['GET'])
def get_student_by_id(student_id):
    """get student by id"""
    student = Student.query.filter_by(public_id = student_id).first()
    
    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Account id `{student_id}` does not exist',
            'student': {}
        }), ERROR_CODE

    return jsonify({
        'status': 'message',
        'student': {
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username,
            'id': student.public_id,
            'teacher': {
                'fname': student.teacher.fname,
                'lname': student.teacher.lname,
                'username': student.teacher.username,
                'id': student.teacher.public_id  
            }
        }
    }), SUCCESS_CODE


@students.route('/api/auth/register/student', methods = ['POST'])
def register_student_account():
    """create stident account"""
    account_info = request.json

    if not account_info:
        return jsonify({
            'status': 'fail',
            'message': 'No account information provided'
        }), ERROR_CODE

    username = account_info.get('username', '')
    password = account_info.get('password', '')
    if not password or not username:
        return jsonify({
            'status': 'fail',
            'message': 'No username or password provided'
        }), ERROR_CODE

    fname = account_info.get('fname', 'No name')
    lname = account_info.get('lname', 'No name')
    public_id = str(uuid.uuid4())
    teacher_username = account_info.get('teacher_username', None)

    # find teacher by username
    teacher = Teacher.query.filter_by(username = teacher_username).first()
    print(teacher)
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account'
        }), ERROR_CODE

    # check if username is uniquer under professor
    existing_student = Student.query.filter_by(username = username).first()
    if existing_student and existing_student.teacher.username == teacher_username:
        return jsonify({
            'status': 'fail',
            'message': 'Username already exists under another student'
        }), ERROR_CODE

    encoded_password = password.encode('utf-8')
    hashed_password = bcrypt.generate_password_hash(encoded_password).decode('utf-8') # password

    student = Student(
        username = username,
        password = hashed_password,
        fname = fname,
        lname = lname,
        public_id = public_id
    )
    student.teacher = teacher

    output = {
        "username": student.username,
        "id": student.public_id,
        "fname": student.fname,
        "lname": student.lname
    }
    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully created',
            'student': output
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account',
            'student': {}
        }), ERROR_CODE


@students.route('/api/account/student/<student_id>', methods = ['PUT', 'POST'])
def update_student_account(student_id):
    """update existing student account"""
    update_info = request.json

    if not update_info:
        return jsonify({
            'status': 'fail',
            'message': 'No account information provided'
        }), ERROR_CODE

    username = update_info['username']
    password = update_info['password']
    fname = update_info.get('fname', 'No name')
    lname = update_info.get('lname', 'No name')
    teacher_username = update_info.get('teacher_username', None)

    # check if account exists
    student = Student.query.filter_by(username = username).first()
    if not student:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    if teacher_username and teacher_username != student.teacher.username:
        new_teacher = Teacher.query.filter_by(username = username).first()

        if not new_teacher:
            return jsonify({
                'status': 'fail',
                'message': 'Account does not exist'
            }), ERROR_CODE

        student.teacher = new_teacher

    # update teacher account
    student.username = username
    student.password = bcrypt.generate_password_hash(password).decode('utf-8')
    student.fname = fname
    student.lname = lname

    output = {
        "username": student.username,
        "id": student.public_id,
        "fname": student.fname,
        "lname": student.lname
    }
    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully created',
            'student': output
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update account'
        }), ERROR_CODE

### Login

@students.route('/api/auth/student/login', methods = ['POST'])
def student_login():
    """login student"""
    credentials = request.json

    if not credentials:
        return jsonify({
            'status': 'fail',
            'message': 'No login credentials provided'
        }), ERROR_CODE

    username = credentials.get('username', '')
    password = credentials.get('password', '')
    if not password or not username:
        return jsonify({
            'status': 'fail',
            'message': 'No username or password provided'
        }), ERROR_CODE
    
    student = Student.query.filter_by(username = username).first()

    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), ERROR_CODE

    encoded_password = password.encode('utf-8')
    if bcrypt.check_password_hash(student.password, encoded_password): # password
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': str(uuid.uuid1()),
            'student': {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            }
        }), SUCCESS_CODE

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), ERROR_CODE
