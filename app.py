# Import necessary libraries from Flask and other packages
from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Importing AI logic from separate Python files
from ai_logic.vectorizer import get_embedding
from ai_logic.matcher import match_documents

# =====================
# FLASK APP SETUP
# =====================
app = Flask(__name__)
app.secret_key = 'jyoti'  # Used for session security

# =====================
# FILE UPLOAD CONFIG
# =====================
UPLOAD_FOLDER = 'uploads'  # Main uploads folder
CANDIDATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'cvs')  # Folder to store CVs
JOBGIVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'jobs')  # Folder to store job requirements
os.makedirs(CANDIDATE_FOLDER, exist_ok=True)  # Create folders if not already there
os.makedirs(JOBGIVER_FOLDER, exist_ok=True)
app.config['CANDIDATE_UPLOADS'] = CANDIDATE_FOLDER
app.config['JOBGIVER_UPLOADS'] = JOBGIVER_FOLDER

# =====================
# DATABASE SETUP
# =====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'  # DB config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  # Initialize SQLAlchemy

# =====================
# DATABASE MODELS
# =====================

# User table: stores both candidates and jobgivers
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # either 'candidate' or 'jobgiver'
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))

# CandidateCV table: stores uploaded CVs by candidates
class CandidateCV(db.Model):
    __tablename__ = 'candidate_cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))  # Stores the selected domain of the CV (e.g., Engineering, IT, etc.)
    user = db.relationship('User', backref='cvs')

# JobRequirement table: stores uploaded job descriptions by jobgivers
class JobRequirement(db.Model):
    __tablename__ = 'job_requirements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))  # Stores the selected domain of the job requirement (must match CV domain)
    user = db.relationship('User', backref='job_requirements')

# =====================
# HELPER FUNCTION
# =====================
# Read the content of a text file (CV or Job file)
def read_file_text(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

# =====================
# ROUTES (WEB PAGES)
# =====================

# Homepage route
@app.route('/')
def homepage():
    return render_template('homepage.html')

# =====================
# LOGIN ROUTE
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login form data
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        # Search for user in database
        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            # Save user info in session
            session['username'] = user.username
            session['role'] = user.role
            # Redirect based on role
            return redirect('/candidate' if role == 'candidate' else '/jobgiver')
        else:
            flash("Invalid login")
    return render_template('login.html')

# =====================
# REGISTER ROUTE
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Create new user from form data
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role=request.form['role'],
            address=request.form.get('address'),
            company_name=request.form.get('company_name')
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html')

# =====================
# CANDIDATE DASHBOARD
# =====================
@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            # Save uploaded CV file
            file = request.files['cv_file']
            domain = request.form.get('domain')  # get selected domain from form
            if file:
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['CANDIDATE_UPLOADS'], filename)
                file.save(path)
                new_cv = CandidateCV(user_id=user.id, filename=filename, domain=domain)  # save domain
                db.session.add(new_cv)
                db.session.commit()
                flash("CV uploaded!")
        cvs = CandidateCV.query.filter_by(user_id=user.id).all()
        return render_template('candidate.html', cvs=cvs, username=user.username)
    return redirect('/')

# =====================
# JOBGIVER DASHBOARD
# =====================
@app.route('/jobgiver', methods=['GET', 'POST'])
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            # Save uploaded Job Description file
            file = request.files['job_file']
            domain = request.form.get('domain')
            if file:
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['JOBGIVER_UPLOADS'], filename)
                file.save(path)
                new_job = JobRequirement(user_id=user.id, filename=filename, domain=domain)  # save domain
                db.session.add(new_job)
                db.session.commit()
                flash("Job uploaded!")
        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=user.username)
    return redirect('/')

# =====================
# DELETE CV (By Candidate)
# =====================
@app.route('/candidate/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    user = User.query.filter_by(username=session['username']).first()
    cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
    if cv:
        path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
        if os.path.exists(path):
            os.remove(path)
        db.session.delete(cv)
        db.session.commit()
    return redirect('/candidate')

# =====================
# DELETE JOB (By JobGiver)
# =====================
@app.route('/jobgiver/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    user = User.query.filter_by(username=session['username']).first()
    job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
    if job:
        path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
        if os.path.exists(path):
            os.remove(path)
        db.session.delete(job)
        db.session.commit()
    return redirect('/jobgiver')

# =====================
# SHOW UPLOADED CV OR JOB FILE
# =====================
@app.route('/uploads/cvs/<filename>')
def uploaded_cv(filename):
    return send_from_directory(app.config['CANDIDATE_UPLOADS'], filename)

@app.route('/uploads/jobs/<filename>')
def uploaded_job(filename):
    return send_from_directory(app.config['JOBGIVER_UPLOADS'], filename)

# =====================
# MATCH CANDIDATES TO JOB (Used by JobGiver)
# =====================
@app.route('/match-candidates', methods=['POST'])
def match_candidates():
    if 'role' in session and session['role'] == 'jobgiver':
        job_id = request.form.get('job_id')
        if not job_id:
            return "Job ID not provided."

        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            return "Job not found."

        job_path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
        if not os.path.exists(job_path):
            return "Job file missing."

        job_text = read_file_text(job_path)
        cvs = CandidateCV.query.filter_by(domain=job.domain).all()  # Same domain

        cv_texts, cv_names = [], []
        for cv in cvs:
            path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                cv_texts.append(read_file_text(path))
                cv_names.append(cv.filename)

        if not cv_texts:
            return "No CVs available for this domain."

        results = match_documents(job_text, cv_texts, cv_names, get_embedding)
        results = [(name, score, job.domain) for name, score in results]

        return render_template('match_results.html', results=results, job_file=job.filename)

    return redirect('/')


# =====================
# MATCH JOBS TO CANDIDATE CV (Used by Candidate)
# =====================
@app.route('/match-jobs', methods=['POST'])
def match_jobs():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()

        cv_id = request.form.get('cv_id')
        if not cv_id:
            return "CV ID not provided."

        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if not cv:
            return "CV not found."

        cv_path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
        if not os.path.exists(cv_path):
            return "CV file missing."

        cv_text = read_file_text(cv_path)
        jobs = JobRequirement.query.filter_by(domain=cv.domain).all()

        job_texts, job_files = [], []
        for job in jobs:
            path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                job_texts.append(read_file_text(path))
                job_files.append(job.filename)

        if not job_texts:
            return "No jobs available for this domain."

        results = match_documents(cv_text, job_texts, job_files, get_embedding)
        results = [(name, score, cv.domain) for name, score in results]

        return render_template('job_matches.html', results=results, cv_file=cv.filename)

    return redirect('/')


# =====================
# RUN FLASK SERVER
# =====================
if __name__ == '__main__':
    app.run(debug=True)

from admin import admin_bp
app.register_blueprint(admin_bp)
