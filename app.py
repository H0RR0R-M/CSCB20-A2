from flask import Flask, render_template, request, redirect, url_for, flash, session , jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import get_flashed_messages

app = Flask(__name__)

# Configure the database (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management

db = SQLAlchemy(app)

# Define the Users model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    user_type = db.Column(db.String(10), nullable=False)  # "student" or "teacher"

# Define the student_marks model
class StudentMarks(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # Foreign key from user 
    module = db.Column(db.String(10), nullable=False, primary_key=True)
    marks = db.Column(db.Integer)
    
# Define the remark_requests model
class RemarkRequests(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # Foreign key from user
    module = db.Column(db.String(10), nullable=False, primary_key=True)
    status = db.Column(db.String(10), nullable=False)

# Define the feedback model
class Feedback(db.Model):
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # Foreign key from user
    q1 = db.Column(db.String(250))
    q2 = db.Column(db.String(250))
    q3 = db.Column(db.String(250))
    q4 = db.Column(db.String(250))


# Initialize the database (Run once to create the tables)
with app.app_context():
    db.create_all()

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user_type = request.form['user_type']
        
        print(f"Name: {name}, Email: {email}, Password: {password}, User Type: {user_type}")  # For testing

        # Check if email already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "error")
            return redirect(url_for('signup'))

        # Add new user to the database
        new_user = Users(name=name, email=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Users.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user session
            flash("Login successful!", "success")
            return redirect(url_for('index'))  # Redirect after login
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('login'))

    get_flashed_messages()
    return render_template('login.html')

# Dashboard after login
@app.route('/index')
def index():
    if 'user_id' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    # Render your index page if the user is logged in
    return render_template('index.html', user_id=session.get('user_id'))  # Ensure you have an index.html template

# Routes for new pages
@app.route('/assignments')
def assignments():
    return render_template('assignments.html', user_id=session.get('user_id'))

@app.route('/labs')
def labs():
    return render_template('labs.html', user_id=session.get('user_id'))

@app.route('/lecture_notes')
def lecture_notes():
    return render_template('lecture_notes.html', user_id=session.get('user_id'))

@app.route('/anon_feedback')
def anon_feedback():
    return render_template('aform.html', user_id=session.get('user_id'))

@app.route('/team')
def team():
    return render_template('team.html', user_id=session.get('user_id'))

@app.route('/studentmark')
def studentmark():
    return render_template('studentmark.html', user_id=session.get('user_id'))

@app.route('/mark_list')
def mark_list():
    return render_template('marklist.html', user_id=session.get('user_id'))

@app.route('/regrades')
def regrades():
    return render_template('regrades.html', user_id=session.get('user_id'))

@app.route('/navigation/<usertype>')
def navigation(usertype):
    if (usertype == "student"):
        return render_template('studentnavigation.html', user_id=session.get('user_id'))
    elif (usertype == "teacher"):
        return render_template('teachernavigation.html', user_id=session.get('user_id'))


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# Success page
@app.route('/success')
def success():
    return "Signup successful! You can now log in."


@app.route("/allstudents", methods=["GET"])
def allstudents():
    students = Users.query.filter_by(user_type="student").all()

    student_list = []
    for student in students:
        student_list.append({"id": student.id, "name": student.name, "email": student.email})

    return jsonify(student_list)

@app.route("/allregrades", methods=["GET"])
def allregrades():
    regrades = RemarkRequests.query.filter_by(status="Pending").all()

    regrade_list = []
    for regrade in regrades:
        regrade_list.append({"id": regrade.student_id, "module": regrade.module, "status": regrade.status})

    return jsonify(regrade_list)



@app.route("/marks/<studentid>/<assessment>", methods=["GET"])
def marks(studentid, assessment):
    mark = StudentMarks.query.filter_by(student_id=int(studentid), module=assessment).first()

    markdata = {}

    if (mark == None):
        markdata = {"id": None, "assessment":None, "mark":-1}
    else:
        markdata = {"id": mark.student_id, "assessment":mark.module, "mark":mark.marks}

    return jsonify(markdata)

@app.route("/allmarks/<studentid>", methods=["GET"])
def allmarks(studentid):
    marks = StudentMarks.query.filter_by(student_id=int(studentid)).all()

    markdata = {}

    mark1 = -1
    mark2 = -1
    mark3 = -1
    mark4 = -1
    mark5 = -1

    if (marks != None):
        for mark in marks:
            if (mark.module == "A1"):
                mark1 = mark.marks
            if (mark.module == "A2"):
                mark2 = mark.marks
            if (mark.module == "A3"):
                mark3 = mark.marks
            if (mark.module == "midterm"):
                mark4 = mark.marks
            if (mark.module == "final"):
                mark5 = mark.marks

    markdata = {"a1": mark1, "a2": mark2, "a3": mark3, "midterm": mark4, "final": mark5}

    return jsonify(markdata)


@app.route("/user/<userid>", methods=["GET"])
def user(userid):
    currentuser = Users.query.filter_by(id=int(userid)).first()

    userdata = {"id": currentuser.id, "name":currentuser.name, "usertype":currentuser.user_type} 

    return jsonify(userdata)

@app.route("/add_regrade/<studentid>/<assessment>", methods=["POST"])
def add_regrade(studentid, assessment):
    newremark = RemarkRequests(student_id = int(studentid), module = assessment, status = "Pending")
    db.session.add(newremark)  
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/add_mark/<studentid>/<assessment>/<newmark>", methods=["POST"])
def add_mark(studentid, assessment, newmark):
    newmark = StudentMarks(student_id = int(studentid), module = assessment, marks = int(newmark))
    db.session.add(newmark)  
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/dorequest/<studentid>/<module>/<status>", methods=["PUT"])
def dorequest(studentid, module, status):
    remark = RemarkRequests.query.filter_by(student_id=int(studentid), module=module)
    remark.status = status
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/update_mark/<studentid>/<module>/<mark>", methods=["PUT"])
def update_mark(studentid, module, mark):
    grade = StudentMarks.query.filter_by(student_id=int(studentid), module=module).first()
    db.session.refresh(grade)
    grade.marks = int(mark)

    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/view_marks", methods=["GET"])
def view_marks():
    marks = StudentMarks.query.all()
    mark_list = [{"student_id": m.student_id, "module": m.module, "mark": m.marks} for m in marks]
    return jsonify(mark_list)





if __name__ == '__main__':
    app.run(debug=True)
