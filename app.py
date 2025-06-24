from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'jyoti'

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
CANDIDATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'cvs')
JOBGIVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'jobs')

# Create folders if not exist
os.makedirs(CANDIDATE_FOLDER, exist_ok=True)
os.makedirs(JOBGIVER_FOLDER, exist_ok=True)

app.config['CANDIDATE_UPLOADS'] = CANDIDATE_FOLDER
app.config['JOBGIVER_UPLOADS'] = JOBGIVER_FOLDER


# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))

# CandidateCV model
from datetime import datetime

class CandidateCV(db.Model):
    __tablename__ = 'candidate_cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='cvs')

# JobRequirement model
class JobRequirement(db.Model):
    __tablename__ = 'job_requirements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='job_requirements')


# Home/Login Page
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            if role == 'candidate':
                return redirect('/candidate')
            else:
                return redirect('/jobgiver')
        else:
            return "Invalid login. Try again."

    return render_template('homepage.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        address = request.form.get('address')
        company_name = request.form.get('company_name')

        new_user = User(
            username=username,
            password=password,
            role=role,
            address=address if role == 'candidate' else None,
            company_name=company_name if role == 'jobgiver' else None
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')

    return render_template('register.html')

# Candidate Page with CV Upload
@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['cv_file']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['CANDIDATE_UPLOADS'], filename)
                file.save(filepath)

                # Save file info to DB
                new_cv = CandidateCV(user_id=user.id, filename=filename)
                db.session.add(new_cv)
                db.session.commit()
                return redirect('/candidate')  # redirect to refresh page and show updated list

        # Show all uploaded CVs of this user
        cvs = CandidateCV.query.filter_by(user_id=user.id).all()
        return render_template('candidate.html', cvs=cvs, username=session['username'])
    return redirect('/')


# Jobgiver Page with Job Requirement Upload
@app.route('/jobgiver', methods=['GET', 'POST'])
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['job_file']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['JOBGIVER_UPLOADS'], filename)
                file.save(filepath)

                # Save to DB
                new_job = JobRequirement(user_id=user.id, filename=filename)
                db.session.add(new_job)
                db.session.commit()

                return redirect('/jobgiver')

        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=session['username'])
    return redirect('/')


# delete CV for candidate
@app.route('/candidate/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if cv:
            # Delete file from disk
            filepath = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            # Delete from DB
            db.session.delete(cv)
            db.session.commit()
        return redirect('/candidate')
    return redirect('/')



# delete job requirement for jobgiver
@app.route('/jobgiver/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if job:
            filepath = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(job)
            db.session.commit()
        return redirect('/jobgiver')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
