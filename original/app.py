from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import get_flashed_messages

app = Flask(__name__)

# Configure the database (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    user_type = db.Column(db.String(10), nullable=False)  # "student" or "teacher"

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
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "error")
            return redirect(url_for('signup'))

        # Add new user to the database
        new_user = User(name=name, email=email, password=password, user_type=user_type)
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

        user = User.query.filter_by(email=email).first()
        
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
    return render_template('index.html')  # Ensure you have an index.html template

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

@app.route('/anon_feedback')
def anon_feedback():
    return render_template('aform.html')

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
