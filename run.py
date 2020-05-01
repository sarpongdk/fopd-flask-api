from fopd import create_app

app = create_app()

if __name__ == "__main__":
    # seedTeacher()
    # seedCourses()
    # seedStudents()
    app.run(debug=True)