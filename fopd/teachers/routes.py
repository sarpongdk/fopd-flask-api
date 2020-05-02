from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Teacher, Student

import uuid

teachers = Blueprint('teachers', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

### Teacher

@teachers.route('/api/teacher', methods = ['GET'])
def get_all_teachers():
    teachers = Teacher.query.all()

    # format output
    output = []
    for teacher in teachers:
        teacher_output = {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'username': teacher.username,
            'public_id': teacher.public_id
        }
        output.append(teacher_output)
    
    return jsonify({
        'status': 'success',
        'length': len(output),
        'teachers_list': output
    }), SUCCESS_CODE

@teachers.route('/api/teacher/<teacher_id>', methods = ['GET'])
def get_teacher_by_id(teacher_id):
    """get teacher by id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account with id {teacher_id} does not exist'
        })

    output = {
        "username": teacher.username,
        "id": teacher.public_id,
        "fname": teacher.fname,
        "lname": teacher.lname
    }
    return jsonify({
        'status': 'success',
        'teacher': output
    }), SUCCESS_CODE


@teachers.route('/api/account/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_teacher_account(teacher_id):
    """update teacher account"""
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

    # check if account exists
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    # update teacher account
    teacher.username = username
    teacher.password = bcrypt.generate_password_hash(password).decode('utf-8')
    teacher.fname = fname
    teacher.lname = lname

    output = {
        "username": teacher.username,
        "id": teacher.public_id,
        "fname": teacher.fname,
        "lname": teacher.lname
    }
    try:
        db.session.add(teacher)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully created',
            'teacher': output
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update account'
        }), ERROR_CODE


### Register account

@teachers.route('/api/auth/register/teacher', methods = ['POST'])
def register_teacher_account():
    """create teacher account"""
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

    encoded_password = password.encode('utf-8')
    hashed_password = bcrypt.generate_password_hash(encoded_password).decode('utf-8') # password

    # check if teacher account already exists
    existing_teacher = Teacher.query.filter_by(username = username).first()
    if existing_teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Username already exists!'
        }), ERROR_CODE

    teacher = Teacher(
        username = username,
        password = hashed_password,
        fname = fname,
        lname = lname,
        public_id = public_id
    )

    output = {
        "username": teacher.username,
        "id": teacher.public_id,
        "fname": teacher.fname,
        "lname": teacher.lname
    }
    try:
        db.session.add(teacher)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully created',
            'teacher': output
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account'
        }), ERROR_CODE

@teachers.route('/api/teacher/<teacher_id>', methods = ['DELETE'])
def delete_teacher_account(teacher_id):
    """delete teacher account"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Account id: `{teacher_id}` has been deleted'
        }), SUCCESS_CODE
    else:
        return jsonify({
            'status': 'fail',
            'message': f'Account id: {teacher_id} does not exist'
        }), ERROR_CODE


### Login

@teachers.route('/api/auth/teacher/login', methods = ['POST'])
def teacher_login():
    """teacher login"""
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

    teacher = Teacher.query.filter_by(username = username).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), ERROR_CODE

    encoded_password = password.encode('utf-8')
    if bcrypt.check_password_hash(teacher.password, encoded_password): # password
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': str(uuid.uuid1()),
            'teacher': {
                'fname': teacher.fname,
                'lname': teacher.lname,
                'username': teacher.username,
                'id': teacher.public_id
            }
        }), SUCCESS_CODE

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), ERROR_CODE
