# Import necessary modules
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask import jsonify, request
from collections import Counter
# Configure Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

awards = {
    "basic_bitch" : "Most basic bitch?",
    "restarted" : "Most restarted?",
    "accoustic" : "Most accoustic?"
}

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    prize_name = db.Column(db.String(20))
    voted_for = db.Column(db.String(20))


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

import copy

@app.route('/dashboard')
def dashboard():
    name = current_user.username
    removal = []
    for key in awards:
        print(name)
        print(key)
        vote = Vote.query.filter_by(username=name, prize_name=key).one_or_none()
        if vote:
            removal.append(key)
    
    awards_copy = copy.deepcopy(awards)
    for key in removal:
        awards_copy.pop(key)

    return render_template('dashboard.html', awards=awards_copy, current_user=current_user)

@app.route('/vote/<award_name>/<award_sentence>')
@login_required
def vote(award_name, award_sentence):
    # Get a list of images from the folder
    image_folder = 'C:\\Users\\senne\\OneDrive\\Bureaublad\\AwardShow\\static\\images'
    print(os.listdir(image_folder))
    print(os.getcwd())
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('png', 'jpg', 'jpeg', 'JPG'))]
    print(image_files)
    return render_template('vote_page.html', award_name=award_name, award_sentence=award_sentence, image_files=image_files)

@app.route('/submit_vote', methods=['POST'])
@login_required
def submit_vote():
    try:
        data = request.get_json()
        person_name = data.get('personName')
        award = data.get('award_name')

        print(f"Voted {person_name}")
        # Implement your logic to handle the vote submission here
        # For example, you can store the votes in the database
        username = current_user.username

        
        new_vote = Vote(username=username, prize_name=award, voted_for=person_name)
        db.session.add(new_vote)

        # Commit the session to persist changes
        db.session.commit()
        return jsonify({'message': 'Vote submitted successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': f"Error submitting vote. {e}"}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', awards=awards)

@app.route('/admin/show_votes/<prize>')
@login_required
def admin_show_votes(prize):
    votes = Vote.query.filter_by(prize_name=prize).all()

    # Count the votes for each person
    vote_counts = Counter(vote.voted_for for vote in votes)

    # Get the top three votes
    top_votes = vote_counts.most_common(3)
    print(top_votes)
    return render_template('admin_show_votes.html', prize_name=prize, top_votes=top_votes)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        existing_user = User.query.filter_by(username='admin').first()
        if not existing_user:
            # Create a new user
            new_user = User(username='admin', password='admin')

            # Add the user to the database session
            db.session.add(new_user)
            db.session.add(User(username='user1', password='user1'))
            db.session.add(User(username='user2', password='user2'))
            db.session.add(User(username='user3', password='user3'))

            # Commit the session to persist changes
            db.session.commit()
        app.run(debug=True)