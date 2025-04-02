from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    module = db.Column(db.String(10), nullable=False)
    marks = db.Column(db.Integer)
    
# Define the remark_requests model
class RemarkRequests(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # Foreign key from user
    module = db.Column(db.String(10), nullable=False)
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
    
# Route for student feedbacks (Instructors only)
@app.route('/feedbacks')
def feedbacks():
    if 'user_id' not in session or session.get('user_type') != 'instructor':
            return redirect(url_for('login'))    
    df = Feedback.query.filter_by(teacher_id=session['user_id']).all()
    print("Feedback Entries:", df)
    return render_template('feedbacks.html', df=df)

# Route for Anonymous feedback
@app.route('/anon_feedback', methods=['GET', 'POST'])
def anon_feedback():
    if request.method == 'POST':
        IID = request.form['instructor']
        qstn1 = request.form['q1']
        qstn2 = request.form['q2']
        qstn3 = request.form['q3']
        qstn4 = request.form['q4']       

        # Add feedback to database
        new_feedback = Feedback(teacher_id=IID, q1=qstn1, q2=qstn2, q3=qstn3, q4=qstn4)
        db.session.add(new_feedback)
        db.session.commit()

        
        return redirect(url_for('anon_feedback'))

    return render_template('feedback.html')

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
            if user.user_type == 'student':
                return redirect(url_for('index'))  # Redirect after login
            else:
                return redirect(url_for('indexI'))  # Redirect after login
           
            
            
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
    return render_template('index.html')  # Ensure you have an index.html template

@app.route('/indexI')
def indexI():
    if 'user_id' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    # Render your index page if the user is logged in
    return render_template('indexI.html')  # Ensure you have an index.html template

# Routes for new pages
@app.route('/assignments')
def assignments():
    return render_template('assignments.html')

@app.route('/labs')
def labs():
    return render_template('labs.html')

@app.route('/lecture_notes')
def lecture_notes():
    return render_template('lecture_notes.html')

@app.route('/team')
def team():
    return render_template('team.html')


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

if __name__ == '__main__':
    app.run(debug=True)

  
    