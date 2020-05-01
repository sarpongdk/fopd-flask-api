from flask import Blueprint, request, jsonify

from fopd import db, bcrypt
from fopd.models import Teacher, Student, Course

import uuid

courses = Blueprint('courses', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

### Courses
@courses.route('/api/course/teacher/<teacher_id>', methods = ['GET'])
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

@courses.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['GET'])
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

@courses.route('/api/course/<course_id>', methods = ['GET'])
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

@courses.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['DELETE'])
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


@courses.route('/api/course/', methods = ['POST'])
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

@courses.route('/api/course/<course_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
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
