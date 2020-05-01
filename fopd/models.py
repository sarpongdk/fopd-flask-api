from fopd import db

class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(60), nullable = False)
    fname = db.Column(db.String(25), default = 'No Name')
    lname = db.Column(db.String(25), default = 'No Name')
    public_id = db.Column(db.String(100), unique = True)

    students = db.relationship('Student', backref = 'teacher', lazy = True, cascade = 'all, delete-orphan')  # or instructor
    courses = db.relationship('Course', backref = 'teacher', lazy = True, cascade = 'all, delete-orphan')

    def __repr__(self):
        return f'<Teacher("{self.username}", "{self.public_id}")>'

class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), nullable = False, unique = True) #edit
    password = db.Column(db.String(60), nullable = False)
    fname = db.Column(db.String(25), default = 'No Name')
    lname = db.Column(db.String(25), default = 'No Name')
    public_id = db.Column(db.String(100), unique = True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id')) #, nullable = False)  # uncomment later

    def __repr__(self):
        return f'<Student("{self.username}", "{self.public_id}")>'

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key = True, autoincrement  = True)
    name = db.Column(db.String(100), nullable = False)
    public_id = db.Column(db.String(100), unique = True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)

    students = db.relationship('Student', backref = 'course', lazy = True, cascade = 'all, delete-orphan')

    def __repr__(self):
        return f'<Course("{self.name}", "{self.public_id}", "{self.students[:4]}")>'
