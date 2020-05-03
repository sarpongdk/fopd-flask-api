from fopd import db

import datetime, uuid

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
    experiments = db.relationship('Experiment', backref = 'teacher', lazy = True, cascade = 'all, delete-orphan')
    assigned_assignments = db.relationship('Assignment', backref = 'teacher', lazy = True, cascade = 'all, delete-orphan')
    devices = db.relationship('Device', backref = 'teacher', lazy = True) # do not cascade

    def __repr__(self):
        return f'<Teacher("{self.username}", "{self.public_id}")>'

    # def __eq__(self, other):
    #     return self._id == other._id and self.public_id == other.public_id

### Many to many
### Student assignments
student_assignments = db.Table('student_assignments',
    db.Column('assignment_id', db.Integer, db.ForeignKey('assignment.id'), nullable = False),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), nullable = False)
)

student_experiments = db.Table('student_experiments',
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id'), nullable = False),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), nullable = False)
)

class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), nullable = False, unique = True) #edit
    password = db.Column(db.String(60), nullable = False)
    fname = db.Column(db.String(25), default = 'No Name')
    lname = db.Column(db.String(25), default = 'No Name')
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id')) #, nullable = False)  # uncomment later
    # experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id')) #, nullable = False) # ask

    assignments = db.relationship('Assignment', secondary = student_assignments, lazy = 'subquery', backref = db.backref('students', lazy = True))
    assignment_responses = db.relationship('AssignmentResponse', backref = 'student', lazy = True, cascade = 'all, delete-orphan')
    observation_responses = db.relationship('ObservationResponse', backref = 'student', lazy = True, cascade = 'all, delete-orphan')
    experiments = db.relationship('Experiment', secondary = student_experiments, lazy = 'subquery', backref = db.backref('students', lazy = True))
    # experiments = db.relationship('Experiment', backref = )

    def __repr__(self):
        return f'<Student("{self.username}", "{self.fname}", "{self.public_id}")>'

    # def __eq__(self, other):
    #     return self._id == other._id and self.public_id == other.public_id

class Device(db.Model):
    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50), nullable = False)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id')) # can be null

    experiments = db.relationship('Experiment', backref = 'device', lazy = True, cascade = 'all, delete-orphan')

    def __repr__(self):
        return f'<Device("{self.name}")>'

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key = True, autoincrement  = True)
    name = db.Column(db.String(100), nullable = False)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)

    students = db.relationship('Student', backref = 'course', lazy = True) #, cascade = 'all, delete-orphan') ask if cascade

    def __repr__(self):
        return f'<Course("{self.name}", "{self.public_id}", "{self.students[:4]}")>'


class Experiment(db.Model):
    __tablename__ = 'experiment'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(80), nullable = False)
    description = db.Column(db.Text, nullable = False)
    plant = db.Column(db.String(50), nullable = False)
    start_date = db.Column(db.Date, nullable = False, default = datetime.date.today)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable = False)

    observations = db.relationship('Observation', backref = 'experiment', lazy = True, cascade = 'all, delete-orphan')
    # students = db.relationship('Student', backref = 'experiment', lazy = False)

    def __repr__(self):
        return f'<Experiment("{self.title}", "{self.start_date}", "{self.public_id}", "{self.students[:4]}")>'


class Assignment(db.Model):
    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    type = db.Column(db.String(50), nullable = False)
    due_date = db.Column(db.Date, nullable = False, default = datetime.date.today)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable = False)

    responses = db.relationship('AssignmentResponse', backref = 'assignment', lazy = True, cascade = 'all, delete-orphan')
    # TODO: test many-to-many works
    def __repr__(self):
        return f'<Assignment("{self.title}", "{self.type}", "{self.public_id}", "{self.teacher.username}")>'

    # def __eq__(self, other):
    #     return self._id == other._id and self._title == other.title and self.public_id == other.public_id


class AssignmentResponse(db.Model):
    __tablename__ = 'assignment_responses'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    response = db.Column(db.Text, nullable = False)
    submitted = db.Column(db.Date, nullable = False, default = datetime.date.today)
    comments = db.Column(db.Text)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable = False)

    def __repr__(self):
        return f'<AssignmentResponse("{self.response}", "{self.student.username}", "{self.public_id}")>'


# observation_responses = db.Table('observation_responses', 
#     db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id'), nullable = False),
#     db.Column('observation_id', db.Integer, db.ForeignKey('observation.id'), nullable = False)
# )

collaborators = db.Table('collaborators', 
    db.Column('observation_id', db.Integer, db.ForeignKey('observation.id'), nullable = False),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), nullable = False)
)

class Observation(db.Model):
    __tablename__ = 'observation'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(50), nullable = False)
    type = db.Column(db.String(30), nullable = False)
    description = db.Column(db.Text, nullable = False)
    units = db.Column(db.String(30), nullable = False)
    updated = db.Column(db.Date, nullable = False, default = datetime.date.today)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'), nullable = False)

    student_collaborators = db.relationship('Student', secondary = collaborators, lazy = 'subquery', backref = db.backref('observations', lazy = True))
    observation_responses = db.relationship('ObservationResponse', backref = 'observation', lazy = True)

class ObservationResponse(db.Model):
    __tablename__ = 'observation_response'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    response = db.Column(db.Text)
    submitted = db.Column(db.Date, nullable = False, default = datetime.date.today)
    editable = db.Column(db.Boolean, nullable = False, default = True)
    public_id = db.Column(db.String(100), unique = True, default = str(uuid.uuid4()))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    observation_id = db.Column(db.Integer, db.ForeignKey('observation.id'), nullable = False)