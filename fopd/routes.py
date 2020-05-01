from fopd import app, db, bcrypt
from flask import request, jsonify

from fopd.models import Teacher, Student, Course, Experiment, Assignment, AssignmentResponse

import uuid, datetime


ERROR_CODE = 400
SUCCESS_CODE = 200

### Student

@app.route('/api/student/<student_id>', methods = ['DELETE'])
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

@app.route('/api/student/teacher/<teacher_id>', methods = ['GET'])
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


@app.route('/api/student/<student_id>', methods = ['GET'])
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


@app.route('/api/auth/register/student', methods = ['POST'])
def register_student_account():
    """create stident account"""
    account_info = request.json

    if not account_info:
        return jsonify({
            'status': 'fail',
            'message': 'No account information provided'
        }), ERROR_CODE

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
        }), ERROR_CODE

    # check if username is uniquer under professor
    existing_student = Student.query.filter_by(username = username).first()
    if existing_student and existing_student.teacher.username == teacher_username:
        return jsonify({
            'status': 'fail',
            'message': 'Username already exists under another student'
        }), ERROR_CODE

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
            'student': output
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create account',
            'student': {}
        }), ERROR_CODE


@app.route('/api/account/student/<student_id>', methods = ['PUT', 'POST'])
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
        'teachers_list': output
    }), SUCCESS_CODE

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
    }), SUCCESS_CODE


@app.route('/api/account/teacher/<teacher_id>', methods = ['PUT', 'POST'])
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


@app.route('/api/auth/register/teacher', methods = ['POST'])
def register_teacher_account():
    """create teacher account"""
    account_info = request.json

    if not account_info:
        return jsonify({
            'status': 'fail',
            'message': 'No account information provided'
        }), ERROR_CODE

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

@app.route('/api/teacher/<teacher_id>', methods = ['DELETE'])
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

@app.route('/api/auth/student/login', methods = ['POST'])
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
    student = Student.query.filter_by(username = username).first()

    if not student:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), ERROR_CODE

    if bcrypt.check_password_hash(student.password, password):
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': token
        }), SUCCESS_CODE

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), ERROR_CODE

@app.route('/api/auth/teacher/login', methods = ['POST'])
def teacher_login():
    """teacher login"""
    credentials = request.json

    if not credentials:
        return jsonify({
            'status': 'fail',
            'message': 'No login credentials provided'
        }), ERROR_CODE

    username = credentials.get('username', None)
    password = credentials.get('password', None)
    teacher = Teacher.query.filter_by(username = username).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Invalid username `{username}`'
        }), ERROR_CODE

    if bcrypt.check_password_hash(teacher.password, password):
        token = 'token'
        return jsonify({
            'status': 'success',
            'message': 'Logged in',
            'token': str(uuid.uuid1())
        }), SUCCESS_CODE

    return jsonify({
            'status': 'fail',
            'message': f'Invalid password'
        }), ERROR_CODE


### Courses
@app.route('/api/course/teacher/<teacher_id>', methods = ['GET'])
def get_teacher_courses(teacher_id):
    """get a list of teacher's courses by id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

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
    """get teacher's course by teacher_id"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), ERROR_CODE      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), ERROR_CODE

    students = []
    for student in course.students:
        students.append({
            'fname': student.fname,
            'lname': student.lname,
            'id': student.public_id,
            'username': student.username
        })

    output = {
        'name': course.name,
        'id': course.public_id,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'username': teacher.username,
            'id': teacher.public_id
        },
        'students': students,
        'num_students': len(students)
    }

    return jsonify({
        'status': 'success',
        'course': output
    }), SUCCESS_CODE

@app.route('/api/course/<course_id>', methods = ['GET'])
def  get_course_by_id(course_id):
    """get course by course_id"""
    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), ERROR_CODE    

    students = []
    for student in course.students:
        students.append({
            'fname': student.fname,
            'lname': student.lname,
            'id': student.public_id,
            'username': student.username
        })

    output = {
        'name': course.name,
        'id': course.public_id,
        'teacher': {
            'fname': course.teacher.fname,
            'lname': course.teacher.lname,
            'username': course.teacher.username,
            'id': course.teacher.public_id
        },
        'students': students,
        'num_students': len(students)
    }   

    return jsonify({
        'status': 'success',
        'course': output
    }), SUCCESS_CODE

@app.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['DELETE'])
def delete_course_by_teacher(course_id, teacher_id):
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), ERROR_CODE      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), ERROR_CODE

    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Course id: `{course_id}` has been deleted'
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        print('ERROR')
        return jsonify({
            'status': 'fail',
            'message': 'Course not deleted'
        }), ERROR_CODE


@app.route('/api/course/', methods = ['POST'])
def register_course():
    course_info = request.json

    if not course_info:
        return jsonify({
            'status': 'fail',
            'message': 'No course information provided'
        }), ERROR_CODE

    course_name = course_info['name']
    teacher_username = course_info['teacher_username']

    teacher = Teacher.query.filter_by(username = teacher_username).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    course = Course(
        name = course_name,
        public_id = str(uuid.uuid4())
    )

    student_usernames = course.get('student_username', [])

    course.teacher = teacher


    student_output = []
    if student_usernames:
        course.students = []
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
    else:
        for student in course.students:
            output = {
                'fname': student.fname,
                'lname': student.lname,
                'username': student.username,
                'id': student.public_id
            }
            student_output.append(output)            

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
                },
                'students': student_output,
                'num_students': len(student_output)
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Course cannot be created'
        }), ERROR_CODE

@app.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_course(course_id, teacher_id):
    """updates course information, assume that everything is being updated"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    course = Course.query.filter_by(public_id = course_id).first()
    if not course:
        return jsonify({
            'status': 'fail',
            'message': 'Course does not exist'
        }), ERROR_CODE      

    if course.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Teacher does not have permission to access this course'
        }), ERROR_CODE

    course_info = request.json

    if not course_info:
        return jsonify({
            'status': 'fail',
            'message': f'No course information provided to update course `{course_id}`'
        }), ERROR_CODE

    student_usernames = course_info.get('student_usernames', [])

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


    # if len(student_output) == 0:
    #     return jsonify({
    #         'status': 'fail',
    #         'message': 'Unable to update course information'
    #     }), ERROR_CODE

    course.name = course_info['name']
    
    try:
        db.session.add(course)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Course updated',
            'course': {
                'name': course.name,
                'id': course.public_id,
                'students': student_output
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update course information'
        }), ERROR_CODE


### Experiment
@app.route('/api/experiment/teacher/<teacher_id>', methods = ['GET'])
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
            'start_date': experiment.start_date,
            'id': experiment.public_id,
            'students': students,
            'num_students': len(students)
        }

        experiments.append(output)

    return jsonify({
        'status': 'success',
        'num_experiments': len(experiments),
        'experiments': experiments
    })

@app.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['GET'])
def get_experiment_by_id(teacher_id, experiment_id):
    """get specific experiment belonging to specific teacher"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment = Experiment.query.filter_by(public_id = experiment_id)
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
        'start_date': experiment.start_date,
        'id': experiment.public_id,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'id': teacher.public_id,
            'username': teacher.username
        },
        'students': students
    }

    return jsonify({
        'status': 'success',
        'experiment': experiment_output
    }), SUCCESS_CODE


@app.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['DELETE'])
def delete_experiment(teacher_id, experiment_id):
    """delete experiment"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()

    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    experiment = Experiment.query.filter_by(public_id = experiment_id)
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

@app.route('/api/experiment/teacher/<teacher_id>', methods = ['POST'])
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

    experiment = Experiment(
        title = experiment_info['title'],
        description = experiment_info['description'],
        plant = experiment_info['plant'],
        public_id = str(uuid.uuid4()),
        start_date = experiment_info.get('start_date', datetime.datetime.utcnow())
    )
    experiment.teacher = teacher

    student_usernames = experiment_info.get('student_usernames', [])

    experiment.students = []
    student_output = []
    for student_username in student_usernames:
        student = Student.query.filter_by(username = student_username).first()

        if student:
            experiment.students.append(student)

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
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to create experiment'
        }), ERROR_CODE

@app.route('/api/experiment/<experiment_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
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

    student_usernames = experiment_info.get('student_usernames', [])

    experiment.students = []
    student_output = []
    for student_username in student_usernames:
        student = Student.query.filter_by(username = student_username).first()

        if student:
            experiment.students.append(student)

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
        }), ERROR_CODE

    experiment.title = experiment_info['title']
    experiment.plant = experiment_info['plant']
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
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': 'Unable to update course information'
        }), ERROR_CODE



### Assignments
@app.route('/api/assignment/student/<student_id>', methods = ['GET'])
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

@app.route('/api/assignment/teacher/<teacher_id>', methods = ['GET'])
def get_all_teacher_assignments(teacher_id):
    """get all teacher assignments"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': 'Account does not exist'
        }), ERROR_CODE

    assignments = teacher.assignments
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

@app.route('/api/assignment/<assignment_id>', methods = ['GET'])
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

@app.route('/api/assignment/teacher/<teacher_id>', methods = ['POST'])
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
    student_usernames = assignment_info.get('student_usernames', [])
    for student_username in student_usernames:
        student = Student.query.filter_by(username = student_username).first()
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



@app.route('/api/assignment/<assignment_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
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

    assignment = Assignment(
        title = assignment_info['title'],
        description = assignment_info['description'],
        type = assignment_info['type'],
        due_date = assignment_info.get('due_date', datetime.datetime.utcnow()),
        public_id = str(uuid.uuid4())
    )  


    student_list = []
    student_usernames = assignment_info.get('student_usernames', [])
    student_list_change = False
    old_student_list = assignment.students
    formatted_old_student_list = []

    for student in old_student_list:
        formatted_old_student_list.append({
            'fname': student.fname,
            'lname': student.lname,
            'id': student.public_id,
            'username': student.username
        })

    for student_username in student_usernames:
        student = Student.query.filter_by(username = student_username)

        if student not in old_student_list:
            student_list_change = True
            break;

    if student_list_change:
        for student_username in student_usernames:
            student = Student.query.filter_by(username = student_username)

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
            'students': student_list if student_list_change else formatted_old_student_list,
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

@app.route('/api/assignment/<assignment_id>/teacher/<teacher_id>', methods = ['DELETE'])
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



### Assignment Responses
@app.route('/api/assignment/<assignment_id>/response', methods = ['GET'])
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


@app.route('/api/assignment/<assignment_id>/response/student/<student_id>', methods = ['GET'])
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
        }
    }

    return jsonify({
        'status': 'success',
        'assignment_response': response_output,
        'student': {
            'id': student.public_id,
            'fname': student.fname,
            'lname': student.lname,
            'username': student.username
        }
    }), SUCCESS_CODE

# @app.route('/api/assignment/<assignment_id>/response/<assignment_response_id>/student/<student_id>', methods = ['PUT', 'POST'])
# def update_student_response(assignment_id, student_id, assignment_response_id):
#     """update student assignment response"""
#     pass

@app.route('/api/assignment/<assignment_id>/response/<assignment_response_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
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