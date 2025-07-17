from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = 'jyoti'

# File upload configuration
UPLOAD_FOLDER = 'uploads'
CANDIDATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'cvs')
JOBGIVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'jobs')
os.makedirs(CANDIDATE_FOLDER, exist_ok=True)
os.makedirs(JOBGIVER_FOLDER, exist_ok=True)
app.config['CANDIDATE_UPLOADS'] = CANDIDATE_FOLDER
app.config['JOBGIVER_UPLOADS'] = JOBGIVER_FOLDER

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =======================
# Database Models
# =======================
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
    user = db.relationship('User', backref='cvs')

class JobRequirement(db.Model):
    __tablename__ = 'job_requirements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='job_requirements')


# =======================
# Routes
# =======================

# Home/Login
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
            return redirect('/candidate' if role == 'candidate' else '/jobgiver')
        else:
            return "Invalid login. Try again."
    return render_template('homepage.html')


# Registration
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


# Candidate Page - Upload CV + Find Matching Jobs
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
                new_cv = CandidateCV(user_id=user.id, filename=filename)
                db.session.add(new_cv)
                db.session.commit()
                flash("CV uploaded successfully!")
                return redirect('/candidate')
        cvs = CandidateCV.query.filter_by(user_id=user.id).all()
        return render_template('candidate.html', cvs=cvs, username=session['username'])
    return redirect('/')


# JobGiver Page - Upload Job File + Find Matching Candidates
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
                new_job = JobRequirement(user_id=user.id, filename=filename)
                db.session.add(new_job)
                db.session.commit()
                flash("Job requirement uploaded! You can now match candidates.")
                return redirect('/jobgiver')
        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=session['username'])
    return redirect('/')


# Delete Candidate CV
@app.route('/candidate/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if cv:
            filepath = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(cv)
            db.session.commit()
        return redirect('/candidate')
    return redirect('/')


# Delete Job Requirement
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

# Serve uploaded files
@app.route('/uploads/cvs/<filename>')
def uploaded_cv(filename):
    return send_from_directory(app.config['CANDIDATE_UPLOADS'], filename)

@app.route('/uploads/jobs/<filename>')
def uploaded_job(filename):
    return send_from_directory(app.config['JOBGIVER_UPLOADS'], filename)



# Helper function to read text files
def read_file_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


# Match Candidates based on latest job uploaded by JobGiver
@app.route('/match-candidates', methods=['GET'])
def match_candidates():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        last_job = JobRequirement.query.filter_by(user_id=user.id).order_by(JobRequirement.upload_date.desc()).first()
        if not last_job:
            return "No job requirement uploaded yet."

        job_text = read_file_text(os.path.join(app.config['JOBGIVER_UPLOADS'], last_job.filename))

        cvs = CandidateCV.query.all()
        cv_texts = []
        cv_names = []

        for cv in cvs:
            path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                text = read_file_text(path)
                cv_texts.append(text)
                cv_names.append(cv.filename)

        if not cv_texts:
            return "No CVs found."

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([job_text] + cv_texts)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        results = list(zip(cv_names, similarity_scores))
        results.sort(key=lambda x: x[1], reverse=True)

        return render_template('match_results.html', results=results, job_file=last_job.filename)
    return redirect('/')


# Match Jobs based on latest CV uploaded by Candidate
@app.route('/match-jobs', methods=['GET'])
def match_jobs():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        last_cv = CandidateCV.query.filter_by(user_id=user.id).order_by(CandidateCV.upload_date.desc()).first()

        if not last_cv:
            return "No CV uploaded yet."

        cv_text = read_file_text(os.path.join(app.config['CANDIDATE_UPLOADS'], last_cv.filename))

        jobs = JobRequirement.query.all()
        job_texts = []
        job_files = []

        for job in jobs:
            path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                text = read_file_text(path)
                job_texts.append(text)
                job_files.append(job.filename)

        if not job_texts:
            return "No job requirements found."

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([cv_text] + job_texts)

        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        results = list(zip(job_files, similarity_scores))
        results.sort(key=lambda x: x[1], reverse=True)

        return render_template('job_matches.html', results=results, cv_file=last_cv.filename)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
