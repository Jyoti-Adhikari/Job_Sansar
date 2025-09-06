# Import necessary libraries from Flask and other packages
from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

# Importing AI logic from separate Python files
from ai_logic.vectorizer import get_embedding
from ai_logic.matcher import match_documents
from ai_logic.extract_text import extract_cv_text, extract_job_text, read_pdf_text

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# =====================
# FLASK APP SETUP
# =====================
app = Flask(__name__)
app.secret_key = 'jyoti'

# =====================
# FILE UPLOAD CONFIG
# =====================
UPLOAD_FOLDER = 'uploads'
CANDIDATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'cvs')
JOBGIVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'jobs')
os.makedirs(CANDIDATE_FOLDER, exist_ok=True)
os.makedirs(JOBGIVER_FOLDER, exist_ok=True)
app.config['CANDIDATE_UPLOADS'] = CANDIDATE_FOLDER
app.config['JOBGIVER_UPLOADS'] = JOBGIVER_FOLDER

# =====================
# DATABASE SETUP
# =====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =====================
# DATABASE MODELS
# =====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))

class CandidateCV(db.Model):
    __tablename__ = 'candidate_cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))
    user = db.relationship('User', backref='cvs')

class JobRequirement(db.Model):
    __tablename__ = 'job_requirements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))
    user = db.relationship('User', backref='job_requirements')

# =====================
# ROUTES
# =====================
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            return redirect('/candidate' if role == 'candidate' else '/jobgiver')
        else:
            flash("Invalid login")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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

@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['cv_file']
            domain = request.form.get('domain')
            if file:
                filename = secure_filename(file.filename)
                if not filename.lower().endswith('.pdf'):
                    flash("Only PDFs allowed!")
                    return redirect('/candidate')
                path = os.path.join(app.config['CANDIDATE_UPLOADS'], filename)
                file.save(path)
                new_cv = CandidateCV(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_cv)
                db.session.commit()
                flash("CV uploaded!")
        cvs = CandidateCV.query.filter_by(user_id=user.id).all()
        return render_template('candidate.html', cvs=cvs, username=user.username)
    return redirect('/')

@app.route('/jobgiver', methods=['GET', 'POST'])
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['job_file']
            domain = request.form.get('domain')
            if file:
                filename = secure_filename(file.filename)
                if not filename.lower().endswith('.pdf'):
                    flash("Only PDFs allowed!")
                    return redirect('/jobgiver')
                path = os.path.join(app.config['JOBGIVER_UPLOADS'], filename)
                file.save(path)
                new_job = JobRequirement(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_job)
                db.session.commit()
                flash("Job uploaded!")
        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=user.username)
    return redirect('/')

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

@app.route('/uploads/cvs/<filename>')
def uploaded_cv(filename):
    return send_from_directory(app.config['CANDIDATE_UPLOADS'], filename)

@app.route('/uploads/jobs/<filename>')
def uploaded_job(filename):
    return send_from_directory(app.config['JOBGIVER_UPLOADS'], filename)

@app.route('/match-candidates', methods=['POST'])
def match_candidates():
    if 'role' in session and session['role'] == 'jobgiver':
        job_id = request.form.get('job_id')
        if not job_id:
            flash("Job ID not provided.")
            return redirect('/jobgiver')

        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            flash("Job not found.")
            return redirect('/jobgiver')

        job_path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
        if not os.path.exists(job_path):
            flash("Job file missing.")
            return redirect('/jobgiver')

        try:
            raw_text = read_pdf_text(job_path)
            job_text = extract_job_text(raw_text)
            logging.debug(f"Extracted job text: {job_text[:200]}...")
            if not job_text.strip():
                flash("No relevant text extracted from job.")
                return redirect('/jobgiver')
        except Exception as e:
            flash(f"Error extracting job text: {str(e)}")
            return redirect('/jobgiver')

        cvs = CandidateCV.query.filter_by(domain=job.domain).all()
        cv_texts, cv_names = [], []
        for cv in cvs:
            path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                try:
                    raw_text = read_pdf_text(path)
                    cv_text = extract_cv_text(raw_text)
                    logging.debug(f"Extracted CV text ({cv.filename}): {cv_text[:200]}...")
                    if cv_text.strip():
                        cv_texts.append(cv_text)
                        cv_names.append(cv.filename)
                except Exception as e:
                    logging.error(f"Error extracting CV {cv.filename}: {str(e)}")

        if not cv_texts:
            flash("No CVs available for this domain.")
            return redirect('/jobgiver')

        results = match_documents(job_text, cv_texts, cv_names, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        # Validate and scale scores
        results = [(name, min(round(max(score, 0.0) * 100, 2), 100.0), job.domain) for name, score in results if score > 0.3]
        logging.debug(f"Final percentage scores: {[(name, score) for name, score, _ in results]}")

        return render_template('match_results.html', results=results, job_file=job.filename)

    return redirect('/')

@app.route('/match-jobs', methods=['POST'])
def match_jobs():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv_id = request.form.get('cv_id')
        if not cv_id:
            flash("CV ID not provided.")
            return redirect('/candidate')

        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if not cv:
            flash("CV not found.")
            return redirect('/candidate')

        cv_path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
        if not os.path.exists(cv_path):
            flash("CV file missing.")
            return redirect('/candidate')

        try:
            raw_text = read_pdf_text(cv_path)
            cv_text = extract_cv_text(raw_text)
            logging.debug(f"Extracted CV text: {cv_text[:200]}...")
            if not cv_text.strip():
                flash("No relevant text extracted from CV.")
                return redirect('/candidate')
        except Exception as e:
            flash(f"Error extracting CV text: {str(e)}")
            return redirect('/candidate')

        jobs = JobRequirement.query.filter_by(domain=cv.domain).all()
        job_texts, job_files = [], []
        for job in jobs:
            path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                try:
                    raw_text = read_pdf_text(path)
                    job_text = extract_job_text(raw_text)
                    logging.debug(f"Extracted job text ({job.filename}): {job_text[:200]}...")
                    if job_text.strip():
                        job_texts.append(job_text)
                        job_files.append(job.filename)
                except Exception as e:
                    logging.error(f"Error extracting job {job.filename}: {str(e)}")

        if not job_texts:
            flash("No jobs available for this domain.")
            return redirect('/candidate')

        results = match_documents(cv_text, job_texts, job_files, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        # Validate and scale scores
        results = [(name, min(round(max(score, 0.0) * 100, 2), 100.0), cv.domain) for name, score in results if score > 0.3]
        logging.debug(f"Final percentage scores: {[(name, score) for name, score, _ in results]}")

        return render_template('job_matches.html', results=results, cv_file=cv.filename)

    return redirect('/')

# =====================
# RUN FLASK SERVER
# =====================
if __name__ == '__main__':
    app.run(debug=True)

from admin import admin_bp
app.register_blueprint(admin_bp)