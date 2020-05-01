from fopd import app, db, bcrypt
from flask import request, jsonify

from fopd.models import Teacher, Student, Course

import uuid


### Student

@app.route('/api/student/<student_id>', methods = ['DELETE', 'POST'])
def delete_student_account(student_id):
    """delete student account by id"""
    student = Student.query.filter_by(public_id = student_id).first()

    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Account id: `{student_id}` has been deleted'
        }), 200
    else:
        return jsonify({
            'status': 'fail',
            'message': f'Account id: {student_id} does not exist'
        }), 400

@app.route('/api/student/<teacher_id>', methods = ['GET'])
def get_all_students_by_teacher(teacher_id):
    """get all students with teacher_id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400
    
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
    }), 200


@app.route('/api/student/<student_id>', methods = ['GET'])
def get_student_by_id(student_id):
    """get student by id"""
    student = Student.query.filter_by(public_id = student_id).first()
    
    if not student:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    return jsonify(student = student), 200


@app.route('/api/auth/register/student', methods = ['POST'])
def register_student_account():
    """create stident account"""
    account_info = request.json
    username = account_info['username']
    password = account_info['password']
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
        }), 400

    # check if username is uniquer under professor
    existing_student = Student.query.filter_by(username = username).first()
    if existing_student and existing_student.teacher.username == teacher_username:
        return jsonify({
            'status': 'fail',
            'message': 'Username already exists under another student'
        }), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

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
            'data': output
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account'
        }), 400


@app.route('/api/account/student/<student_id>', methods = ['PUT', 'POST'])
def update_student_account(student_id):
    """update existing student account"""
    update_info = request.json
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
        }), 400

    if teacher_username and teacher_username != student.teacher.username:
        new_teacher = Teacher.query.filter_by(username = username).first()

        if not new_teacher:
            return jsonify({
                'status': 'fail',
                'message': 'Account does not exist'
            }), 400

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
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update account'
        }), 400

### Teacher

@app.route('/api/teacher', methods = ['GET'])
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
        'teachers': output
    }), 200

@app.route('/api/teacher/<teacher_id>', methods = ['GET'])
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
    }), 200


@app.route('/api/account/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_teacher_account(teacher_id):
    """update teacher account"""
    update_info = request.json
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
        }), 400

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
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update account'
        }), 400


@app.route('/api/auth/register/teacher', methods = ['POST'])
def register_teacher_account():
    """create teacher account"""
    account_info = request.json
    username = account_info['username']
    password = account_info['password']
    fname = account_info.get('fname', 'No name')
    lname = account_info.get('lname', 'No name')
    public_id = str(uuid.uuid4())
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # check if teacher account already exists
    existing_teacher = Teacher.query.filter_by(username = username).first()
    if existing_teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Username already exists!'
        }), 400

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
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account'
        }), 400

@app.route('/api/teacher/<teacher_id>', methods = ['DELETE', 'POST'])
def delete_teacher_account(teacher_id):
    """delete teacher account"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Account id: `{teacher_id}` has been deleted'
        }), 200
    else:
        return jsonify({
            'status': 'fail',
            'message': f'Account id: {teacher_id} does not exist'
        }), 400


### Login

@app.route('/api/auth/student/login', methods = ['POST'])
def student_login():
    """login student"""
    credentials = request.json
    username = credentials.get('username', None)
    password = credentials.get('password', None)
    student = Student.query.filter_by(username = username).first()

    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), 400

    if bcrypt.check_password_hash(student.password, password):
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': token
        }), 200

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), 400

@app.route('/api/auth/teacher/login', methods = ['POST'])
def teacher_login():
    """teacher login"""
    credentials = request.json
    username = credentials.get('username', None)
    password = credentials.get('password', None)
    teacher = Teacher.query.filter_by(username = username).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), 400

    if bcrypt.check_password_hash(teacher.password, password):
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': token
        }), 200

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), 400


### Courses
@app.route('/api/course/teacher/<teacher_id>', methods = ['GET'])
def get_teacher_courses(teacher_id):
    """get a list of teacher's courses by id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    formatted_courses = []
    for course in teacher.courses:
        students = []

        for student in course.students:
            student_output = {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'public_id': student.public_id
            }
            students.append(student_output)
        
        course_output = {
            'name': course.name,
            'id': course.public_id,
            'students': students,
            'num_students': len(students),
            'teacher': {
                'fname': teacher.fname,
                'lname': teacher.lname,
                'username': teacher.username,
                'public_id': teacher.public_id
            }
        }
        formatted_courses.append(course_output)
    return jsonify({
        'status': 'success',
        'courses': formatted_courses
    })

@app.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['GET'])
def  get_teacher_course_by_id(course_id, teacher_id):
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), 400      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), 400

    output = {
        'name': course.name,
        'id': course.public_id,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'username': teacher.username,
            'id': teacher.public_id
        }
    }

    return jsonify({
        'status': 'success',
        'course': output
    }), 200

@app.route('/api/course/<course_id>', methods = ['GET'])
def  get_course_by_id(course_id):
    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), 400    

    output = {
        'name': course.name,
        'id': course.public_id,
        'teacher': {
            'fname': course.teacher.fname,
            'lname': course.teacher.lname,
            'username': course.teacher.username,
            'id': course.teacher.public_id
        }
    }   

    return jsonify({
        'status': 'success',
        'course': output
    }), 200

@app.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['DELETE', 'POST'])
def delete_course_by_teacher(course_id, teacher_id):
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), 400      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), 400

    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Course id: `{course_id}` has been deleted'
        }), 200
    except Exception as e:
        print(e)
        print('ERROR')
        return jsonify({
            'status': 'fail',
            'message': 'Course not deleted'
        }), 400


@app.route('/api/course/', methods = ['POST'])
def register_course():
    course_info = request.json
    course_name = course_info['name']
    teacher_username = course_info['teacher_username']

    teacher = Teacher.query.filter_by(username = teacher_username).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    course = Course(
        name = course_name,
        public_id = str(uuid.uuid4())
    )

    course.teacher = teacher

    try:
        db.session.add(course)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Successfully registered course',
            'course': {
                'name': course.name,
                'id': course.public_id,
                'teacher': {
                    'fname': teacher.fname,
                    'lname': teacher.lname,
                    'username': teacher.username,
                    'id': teacher.public_id
                }
            }
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Course cannot be created'
        }), 400

@app.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['PUT'])
def update_course(course_id, teacher_id):
    """updates course information, assume that everything is being updated"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), 400

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), 400      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), 400

    course_info = request.json
    student_usernames = course_info['student_usernames']

    course.students = []
    student_output = []
    for student_username in student_usernames:
        student = Student.query.filter_by(username = student_username).first()

        if student:
            course.students.append(student)

            output = {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            }
            student_output.append(output)


    if len(student_output) == 0:
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update course information'
        }), 400

    course.name = course_info['name']
    #db.session.add(course)
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Course updated',
            'course': {
                'name': course.name,
                'id': course.public_id,
                'students': student_output
            }
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update course information'
        }), 400

