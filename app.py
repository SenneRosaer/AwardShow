# Import necessary modules
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask import jsonify, request
# Configure Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Form for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Form for voting
class VoteForm(FlaskForm):
    vote = StringField('Vote', validators=[DataRequired()])
    submit = SubmitField('Submit Vote')

# Flask-Login callback to load a user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user.password)
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    form = VoteForm()
    return render_template('dashboard.html', form=form)

@app.route('/vote')
@login_required
def vote():
    # Get a list of images from the folder
    image_folder = 'C:\\Users\\senne\\OneDrive\\Bureaublad\\AwardShow\\static\\images'
    print(os.listdir(image_folder))
    print(os.getcwd())
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('png', 'jpg', 'jpeg', 'JPG'))]
    print(image_files)
    return render_template('vote_page.html', image_files=image_files)

@app.route('/submit_vote', methods=['POST'])
@login_required
def submit_vote():
    try:
        data = request.get_json()
        person_name = data.get('personName')
        print(f"Voted {person_name}")
        # Implement your logic to handle the vote submission here
        # For example, you can store the votes in the database

        return jsonify({'message': 'Vote submitted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': 'Error submitting vote.'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        existing_user = User.query.filter_by(username='admin').first()
        if not existing_user:
            # Create a new user
            new_user = User(username='admin', password='admin')

            # Add the user to the database session
            db.session.add(new_user)

            # Commit the session to persist changes
            db.session.commit()
        app.run(debug=True)