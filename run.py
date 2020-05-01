from fopd import app, db

from fopd.models import Teacher, Student, Course

import uuid

db.session.close()
db.drop_all()
db.create_all()
db.session.commit()

teachers = [
    {
        'fname': 'Jacob',
        'lname': 'Sukhodolsky',
        'username': 'sukhodolsky',
        'password': '12345'
    },
        {
        'fname': 'Erin',
        'lname': 'Chambers',
        'username': 'chambers',
        'password': 'chambers'
    },
    {
        'fname': 'Reza',
        'lname': 'Tourani',
        'username': 'tourani',
        'password': 'security'
    },
    {
        'fname': 'Kevin',
        'lname': 'Scannell',
        'username': 'kscannee',
        'password': 'ML'
    },
    {
        'fname': 'Kate',
        'lname': 'Holdener',
        'username': 'ekaterina',
        'password': 'design'
    }
]

students = [
    # {
    #     'fname': 'Aidan',
    #     'lname': 'Latham',
    #     'username': 'latham',
    #     'password': 'student',
    #     'teacher_username': 'chambers'
    # },
    {
        'fname': 'David',
        'lname': 'Sarpong',
        'username': 'dsarp',
        'password': '12345',
        'teacher_username': 'chambers'
    },
    {
        'fname': 'Aaron',
        'lname': 'Oofs',
        'username': 'oofs',
        'password': 'oofs',
        'teacher_username': 'ekaterina'
    },
    {
        'fname': 'Rasika',
        'lname': 'Scarff',
        'username': 'scarffrj',
        'password': 'password',
        'teacher_username': 'tourani'
    },
    {
        'fname': 'Kenneth',
        'lname': 'Harley',
        'username': 'kharley',
        'password': 'student',
        'teacher_username': 'tourani'
    },
]

courses = [
    {
        "name": "Computer Security",
        "teacher_username": "tourani"
    },
    {
        "name": "Software Engineering",
        "teacher_username": "ekaterina"
    },
    {
        "name": "Databases",
        "teacher_username": "sukhodolsky"
    },
    {
        "name": "Machine Learning",
        "teacher_username": "kscannee"
    }
]

def seedTeacher():
    for info in teachers:
        teacher = Teacher(
            username = info['username'],
            password = info['password'],
            fname = info['fname'],
            lname = info['lname'],
            public_id = str(uuid.uuid4())
        )

        db.session.add(teacher)
        db.session.commit()

   

def seedStudents():
    for info in students:
        teacher = Teacher.query.filter_by(username = info['teacher_username']).first()
        student = Student(
            username = info['username'],
            password = info['password'],
            fname = info['fname'],
            lname = info['lname'],
            public_id = str(uuid.uuid4()),
        )
        

        student.teacher = teacher
        if len(teacher.courses) > 0:
            student.course = teacher.courses[0]

        db.session.add(student)
        db.session.commit()

def seedCourses():
    for info in courses:
        teacher = Teacher.query.filter_by(username = info['teacher_username']).first()

        course = Course(
            name = info['name'],
            public_id = str(uuid.uuid4())
        )

        course.teacher = teacher

        db.session.add(course)
        db.session.commit()

if __name__ == "__main__":
    seedTeacher()
    seedCourses()
    seedStudents()
    app.run(debug=True)