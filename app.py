# Import necessary libraries from Flask and other packages
from flask import Flask, render_template, request, redirect, session, flash, send_from_directory, url_for, jsonify
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
app.secret_key = os.urandom(24)  # Secure random key for production

# =====================
# FILE UPLOAD CONFIG
# =====================
UPLOAD_FOLDER = 'Uploads'
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
    role = db.Column(db.String(20), nullable=False)  # candidate, jobgiver, admin
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='feedback')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requirements.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'cv' or 'job'
    file_id = db.Column(db.Integer, nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'inquiry', 'invite', 'application'
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    related_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Shortlist(db.Model):
    __tablename__ = 'shortlists'
    id = db.Column(db.Integer, primary_key=True)
    jobgiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cv_id = db.Column(db.Integer, db.ForeignKey('candidate_cvs.id'), nullable=False)
    shortlisted_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requirements.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

class CareerPath(db.Model):
    __tablename__ = 'career_paths'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.JSON)
    average_salary_min = db.Column(db.Integer)
    average_salary_max = db.Column(db.Integer)
    growth_outlook = db.Column(db.String(50))
    experience_level = db.Column(db.String(50))
    domain = db.Column(db.String(100))

class UserSkills(db.Model):
    __tablename__ = 'user_skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency_level = db.Column(db.String(50))
    years_experience = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='skills')

# =====================
# HELPER FUNCTIONS 
# =====================
def get_cv_filename(cv_id):
    cv = CandidateCV.query.get(cv_id)
    return cv.filename if cv else "unknown.pdf"

def get_job_filename(job_id):
    job = JobRequirement.query.get(job_id)
    return job.filename if job else "unknown.pdf"

def get_filename_from_message(message):
    """
    Get the correct filename based on message type and file_type
    """
    if message.message_type == 'application':
        # For applications: file_id is job_id, file_type is 'job'
        if message.file_type == 'job':
            job = JobRequirement.query.get(message.file_id)
            return job.filename if job else "unknown.pdf"
    elif message.message_type == 'invite':
        # For invites: file_id is cv_id, file_type is 'cv'  
        if message.file_type == 'cv':
            cv = CandidateCV.query.get(message.file_id)
            return cv.filename if cv else "unknown.pdf"
    
    return "unknown.pdf"

def get_file_url_from_message(message):
    """
    Get the correct file URL based on message type
    """
    filename = get_filename_from_message(message)
    
    if message.message_type == 'application' and message.file_type == 'job':
        return url_for('uploaded_job', filename=filename)
    elif message.message_type == 'invite' and message.file_type == 'cv':
        return url_for('uploaded_cv', filename=filename)
    elif message.file_type == 'cv':
        return url_for('uploaded_cv', filename=filename)
    elif message.file_type == 'job':
        return url_for('uploaded_job', filename=filename)
    
    return "#"

def get_sender_cv_filename(sender_id):
    """Get the first CV filename from a sender (user)"""
    sender = User.query.get(sender_id)
    if sender and sender.cvs:
        return sender.cvs[0].filename
    return "unknown.pdf"

def get_sender_job_filename(sender_id):
    """Get the first job filename from a sender (user)"""
    sender = User.query.get(sender_id)
    if sender and sender.job_requirements:
        return sender.job_requirements[0].filename
    return "unknown.pdf"

def notify(user_id, title, body, type_, related_id):
    n = Notification(user_id=user_id, title=title, body=body, type=type_, related_id=related_id)
    db.session.add(n)
    db.session.commit()

# Make functions available to templates
@app.context_processor
def utility_processor():
    return dict(
        get_cv_filename=get_cv_filename,
        get_job_filename=get_job_filename,
        get_filename_from_message=get_filename_from_message,
        get_file_url_from_message=get_file_url_from_message,
        get_sender_cv_filename=get_sender_cv_filename,
        get_sender_job_filename=get_sender_job_filename
    )

# =====================
# ROUTES
# =====================
@app.route('/')
def homepage():
    # Check if user is logged in and redirect to appropriate dashboard
    if 'username' in session and 'role' in session:
        if session['role'] == 'candidate':
            return redirect(url_for('precandidate'))
        elif session['role'] == 'jobgiver':
            return redirect(url_for('prejobgiver'))
        elif session['role'] == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    
    # If not logged in, show public homepage
    return render_template('homepage.html')

@app.route('/about')
def about():
    return render_template('about.html')

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
            next_url = request.form.get('next') or ('/precandidate' if role == 'candidate' else '/prejobgiver' if role == 'jobgiver' else '/admin')
            return redirect(next_url)
        else:
            flash("Invalid login credentials.", "error")
    next_url = request.args.get('next', '')
    return render_template('login.html', next=next_url)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'username' not in session:
        flash("You must log in to submit feedback.", "error")
        return redirect(url_for('login', next=request.url))

    if request.method == 'POST':
        message = request.form.get('message')
        if not message or not message.strip():
            flash("Feedback message is required!", "error")
            return render_template('contact.html')
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for('login'))
        feedback = Feedback(user_id=user.id, message=message)
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        address = request.form.get('address')
        company_name = request.form.get('company_name')

        # Restrict admin role to username=jyoti, password=jyoti
        if role == 'admin' and (username != 'jyoti' or password != 'jyoti'):
            flash("Admin role is restricted to username 'jyoti' and password 'jyoti'.", "error")
            return render_template('register.html')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return render_template('register.html')

        user = User(
            username=username,
            password=password,
            role=role,
            address=address,
            company_name=company_name
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/precandidate', methods=['GET', 'POST'])
def precandidate():
    # Fetch all job files uploaded by job givers
    jobs = JobRequirement.query.all()

    # If candidate uploads a CV
    if request.method == 'POST':
        file = request.files.get('cv_file')
        domain = request.form.get('domain')

        if not file:
            flash("Please select a CV file.", "error")
            return redirect(url_for('precandidate'))

        # Only allow PDF files
        if not file.filename.lower().endswith('.pdf'):
            flash("Only PDF files are allowed!", "error")
            return redirect(url_for('precandidate'))

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['CANDIDATE_UPLOADS'], filename)
        file.save(save_path)

        flash("CV uploaded successfully!", "success")
        return redirect(url_for('precandidate'))

    # Show the page
    return render_template('precandidate.html', jobs=jobs)

@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()

        # Fetch all job givers' uploaded job requirement PDFs
        jobs = JobRequirement.query.all()

        if request.method == 'POST':
            file = request.files['cv_file']
            domain = request.form.get('domain')
            if file:
                filename = secure_filename(file.filename)
                if not filename.lower().endswith('.pdf'):
                    flash("Only PDFs allowed!", "error")
                    return redirect(url_for('candidate'))

                path = os.path.join(app.config['CANDIDATE_UPLOADS'], filename)
                file.save(path)

                new_cv = CandidateCV(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_cv)
                db.session.commit()

                flash("CV uploaded!", "success")

        cvs = CandidateCV.query.filter_by(user_id=user.id).all()

        # pass jobs to template
        return render_template(
            'candidate.html',
            cvs=cvs,
            username=user.username,
            jobs=jobs
        )

    return redirect(url_for('login'))

@app.route('/jobgiver', methods=['GET', 'POST'])
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['job_file']
            domain = request.form.get('domain')
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['JOBGIVER_UPLOADS'], filename)
                file.save(path)
                new_job = JobRequirement(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_job)
                db.session.commit()
                flash("Job uploaded!", "success")
        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=user.username)
    return redirect(url_for('login'))

@app.route('/prejobgiver')
def prejobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        cvs = CandidateCV.query.all()
        user = User.query.filter_by(username=session['username']).first()
        return render_template("prejobgiver.html", cvs=cvs, username=user.username)
    return redirect(url_for("login"))

@app.route('/candidate/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if cv:
            path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(cv)
            db.session.commit()
            flash("CV deleted successfully!", "success")
        else:
            flash("CV not found!", "error")
    return redirect(url_for('candidate'))

@app.route('/jobgiver/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if job:
            path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(job)
            db.session.commit()
            flash("Job deleted successfully!", "success")
        else:
            flash("Job not found!", "error")
    return redirect(url_for('jobgiver'))

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
            flash("Job ID not provided.", "error")
            return redirect(url_for('jobgiver'))

        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            flash("Job not found.", "error")
            return redirect(url_for('jobgiver'))

        job_path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
        if not os.path.exists(job_path):
            flash("Job file missing.", "error")
            return redirect(url_for('jobgiver'))

        try:
            raw_text = read_pdf_text(job_path)
            job_text = extract_job_text(raw_text)  # Uses enhanced extraction
            logging.debug(f"Extracted job text: {job_text[:200]}...")
            if not job_text.strip():
                flash("No relevant text extracted from job.", "error")
                return redirect(url_for('jobgiver'))
        except Exception as e:
            flash(f"Error extracting job text: {str(e)}", "error")
            return redirect(url_for('jobgiver'))

        cvs = CandidateCV.query.filter_by(domain=job.domain).all()
        cv_texts, cv_names = [], []
        for cv in cvs:
            path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                try:
                    raw_text = read_pdf_text(path)
                    cv_text = extract_cv_text(raw_text)  # Uses enhanced extraction
                    logging.debug(f"Extracted CV text ({cv.filename}): {cv_text[:200]}...")
                    if cv_text.strip():
                        cv_texts.append(cv_text)
                        cv_names.append(cv.filename)
                except Exception as e:
                    logging.error(f"Error extracting CV {cv.filename}: {str(e)}")

        if not cv_texts:
            flash("No CVs available for this domain.", "error")
            return redirect(url_for('jobgiver'))

        # Use simple cosine similarity matching (proven approach)
        results = match_documents(job_text, cv_texts, cv_names, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        
        # Validate and scale scores
        results = [(name, min(round(max(score, 0.0) * 100, 2), 100.0), job.domain) for name, score in results if score > 0.3]
        logging.debug(f"Final percentage scores: {[(name, score) for name, score, _ in results]}")

        matched_cvs = []
        for cv_file, score, domain in results:
            cv = CandidateCV.query.filter_by(filename=cv_file).first()
            matched_cvs.append((cv_file, score, domain, int(cv.id) if cv else 0))

        cv_ids = [c[3] for c in matched_cvs if c[3] is not None]
       
        shortlist_map = {s.cv_id: True for s in Shortlist.query.filter_by(jobgiver_id=user.id).all()}

        return render_template(
            'match_results.html',
            results=matched_cvs,
            job_file=job.filename,
            cv_ids=cv_ids,
            shortlist_map=shortlist_map
        )

    return redirect(url_for('login'))

@app.route('/match-jobs', methods=['POST'])
def match_jobs():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv_id = request.form.get('cv_id')
        if not cv_id:
            flash("CV ID not provided.", "error")
            return redirect(url_for('candidate'))

        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if not cv:
            flash("CV not found.", "error")
            return redirect(url_for('candidate'))

        cv_path = os.path.join(app.config['CANDIDATE_UPLOADS'], cv.filename)
        if not os.path.exists(cv_path):
            flash("CV file missing.", "error")
            return redirect(url_for('candidate'))

        try:
            raw_text = read_pdf_text(cv_path)
            cv_text = extract_cv_text(raw_text)  # Uses enhanced extraction
            logging.debug(f"Extracted CV text: {cv_text[:200]}...")
            if not cv_text.strip():
                flash("No relevant text extracted from CV.", "error")
                return redirect(url_for('candidate'))
        except Exception as e:
            flash(f"Error extracting CV text: {str(e)}", "error")
            return redirect(url_for('candidate'))

        jobs = JobRequirement.query.filter_by(domain=cv.domain).all()
        job_texts, job_files = [], []
        for job in jobs:
            path = os.path.join(app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                try:
                    raw_text = read_pdf_text(path)
                    job_text = extract_job_text(raw_text)  # Uses enhanced extraction
                    logging.debug(f"Extracted job text ({job.filename}): {job_text[:200]}...")
                    if job_text.strip():
                        job_texts.append(job_text)
                        job_files.append(job.filename)
                except Exception as e:
                    logging.error(f"Error extracting job {job.filename}: {str(e)}")

        if not job_texts:
            flash("No jobs available for this domain.", "error")
            return redirect(url_for('candidate'))

        # Use simple cosine similarity matching (proven approach)
        results = match_documents(cv_text, job_texts, job_files, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        
        # Validate and scale scores
        results = [(name, min(round(max(score, 0.0) * 100, 2), 100.0), cv.domain) for name, score in results if score > 0.3]
        logging.debug(f"Final percentage scores: {[(name, score) for name, score, _ in results]}")

        matched_jobs = []
        for job_file, score, domain in results:
            job = JobRequirement.query.filter_by(filename=job_file).first()
            matched_jobs.append((job_file, score, domain, int(job.id) if job else 0))

        job_ids = [j[3] for j in matched_jobs if j[3] is not None]
       
        saved_map = {s.job_id: True for s in SavedJob.query.filter_by(candidate_id=user.id).all()}

        return render_template(
            'job_matches.html',
            results=matched_jobs,
            cv_file=cv.filename,
            job_ids=job_ids,
            saved_map=saved_map         
        )

    return redirect(url_for('login'))

# === INBOX ===
@app.route('/inbox')
def inbox():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    # Get messages where user is receiver ONLY (not sender)
    messages = Message.query.filter(
        Message.receiver_id == user.id
    ).order_by(Message.sent_at.desc()).all()
    
    # Count unread messages (where user is receiver and message is unread)
    unread_count = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    
    return render_template('inbox.html', messages=messages, unread_count=unread_count, current_user=user)

@app.route('/inbox-data')
def inbox_data():
    if 'username' not in session:
        return jsonify({'unread': 0, 'messages': []})
    
    user = User.query.filter_by(username=session['username']).first()
    
    messages = Message.query.filter(
        (Message.receiver_id == user.id) | (Message.sender_id == user.id)
    ).order_by(Message.sent_at.desc()).limit(20).all()

    msg_list = []
    for m in messages:
        msg_list.append({
            'id': m.id,
            'sender': m.sender.username,
            'receiver': m.receiver.username,
            'message': m.message,
            'message_type': m.message_type,
            'time': m.sent_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': m.is_read
        })

    unread_count = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return jsonify({'unread': unread_count, 'messages': msg_list})

# === MARK MESSAGE AS READ ===
@app.route('/mark-message-read', methods=['POST'])
def mark_message_read():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    message_id = data.get('message_id')
    
    try:
        message_id = int(message_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid Message ID"}), 400
        
    user = User.query.filter_by(username=session['username']).first()
    message = Message.query.filter_by(id=message_id, receiver_id=user.id).first()
    
    if not message:
        return jsonify({"error": "Message not found"}), 404
        
    message.is_read = True
    db.session.commit()
    
    return jsonify({"success": "Message marked as read"})

# === APPLY NOW (One-way notification) ===
@app.route('/apply', methods=['POST'])
def apply_now():
    if session.get('role') != 'candidate':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    job_id = data.get('job_id')
    
    # Convert to integer if it's a string
    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid Job ID"}), 400
    
    user = User.query.filter_by(username=session['username']).first()
    job = JobRequirement.query.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if Application.query.filter_by(candidate_id=user.id, job_id=job_id).first():
        return jsonify({'error': 'Already applied'}), 400

    # Create application record
    app = Application(candidate_id=user.id, job_id=job_id)
    db.session.add(app)
    
    # Create one-way notification message to job giver
    application_message = f"{user.username} has applied for your job: {job.filename}"
    msg = Message(
        sender_id=user.id, 
        receiver_id=job.user_id,
        message=application_message, 
        file_type='job', 
        file_id=job_id,
        message_type='application'
    )
    db.session.add(msg)
    
    # Commit both application and message
    db.session.commit()

    # Notify job giver
    notify(job.user_id, "New Application", f"{user.username} applied to your job", 'application', app.id)

    return jsonify({'success': 'Applied successfully!'})

# === SHORTLIST CV ===
@app.route('/shortlist-cv', methods=['POST'])
def shortlist_cv():
    if session.get('role') != 'jobgiver': 
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    cv_id = data.get('cv_id')
    
    # Convert to integer if it's a string
    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400
    
    user = User.query.filter_by(username=session['username']).first()
    
    if Shortlist.query.filter_by(jobgiver_id=user.id, cv_id=cv_id).first():
        return jsonify({"error": "Already shortlisted"}), 400
        
    db.session.add(Shortlist(jobgiver_id=user.id, cv_id=cv_id))
    db.session.commit()
    return jsonify({"success": "Shortlisted!"})

# === REMOVE FROM SHORTLIST ===
@app.route('/remove-shortlist', methods=['POST'])
def remove_shortlist():
    if session.get('role') != 'jobgiver': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    cv_id = data.get('cv_id')
    
    # Convert to integer if it's a string
    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400
        
    user = User.query.filter_by(username=session['username']).first()
        
    item = Shortlist.query.filter_by(jobgiver_id=user.id, cv_id=cv_id).first()
    if not item: 
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": "Removed from shortlist"})

# === SAVE JOB ===
@app.route('/save-job', methods=['POST'])
def save_job():
    if session.get('role') != 'candidate': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    job_id = data.get('job_id')
    
    # Convert to integer if it's a string
    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid Job ID"}), 400
        
    user = User.query.filter_by(username=session['username']).first()
        
    if SavedJob.query.filter_by(candidate_id=user.id, job_id=job_id).first():
        return jsonify({"error": "Already saved"}), 400
        
    db.session.add(SavedJob(candidate_id=user.id, job_id=job_id))
    db.session.commit()
    return jsonify({"success": "Saved!"})

# === REMOVE SAVED JOB ===
@app.route('/remove-saved-job', methods=['POST'])
def remove_saved_job():
    if session.get('role') != 'candidate': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    job_id = data.get('job_id')
    
    # Convert to integer if it's a string
    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid Job ID"}), 400
        
    user = User.query.filter_by(username=session['username']).first()
        
    item = SavedJob.query.filter_by(candidate_id=user.id, job_id=job_id).first()
    if not item: 
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": "Removed from saved"})

# === VIEW SHORTLISTED ===
@app.route('/shortlisted')
def shortlisted():
    if session.get('role') != 'jobgiver': 
        return redirect(url_for('login'))
        
    user = User.query.filter_by(username=session['username']).first()
    shortlists = Shortlist.query.filter_by(jobgiver_id=user.id).all()
    
    items = []
    for shortlist in shortlists:
        cv = CandidateCV.query.get(shortlist.cv_id)
        if cv:
            cv_user = User.query.get(cv.user_id)
            items.append((shortlist, cv, cv_user))
    
    return render_template('shortlisted.html', items=items)

# === VIEW SAVED JOBS ===
@app.route('/saved-jobs')
def saved_jobs():
    if session.get('role') != 'candidate': 
        return redirect(url_for('login'))
        
    user = User.query.filter_by(username=session['username']).first()
    saved_jobs = SavedJob.query.filter_by(candidate_id=user.id).all()
    
    items = []
    for saved in saved_jobs:
        job = JobRequirement.query.get(saved.job_id)
        if job:
            job_user = User.query.get(job.user_id)
            items.append((saved, job, job_user))
    
    return render_template('saved_jobs.html', items=items)

# === API: Counts for badge ===
@app.route('/api/counts')
def api_counts():
    if 'username' not in session: 
        return jsonify({})
        
    user = User.query.filter_by(username=session['username']).first()
    out = {}
    if session['role'] == 'jobgiver':
        out['shortlist'] = Shortlist.query.filter_by(jobgiver_id=user.id).count()
    elif session['role'] == 'candidate':
        out['saved'] = SavedJob.query.filter_by(candidate_id=user.id).count()
    return jsonify(out)

# === SEND INVITE (One-way notification) ===
@app.route('/send-invite', methods=['POST'])
def send_invite():
    if session.get('role') != 'jobgiver':
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    cv_id = data.get('cv_id')

    # Convert to integer if it's a string
    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400

    jobgiver = User.query.filter_by(username=session['username']).first()
    cv = CandidateCV.query.get(cv_id)
    
    if not cv:
        return jsonify({"error": "CV not found"}), 404
        
    candidate = cv.user

    # Create one-way notification message to candidate ONLY
    invite_message = f"{jobgiver.company_name or jobgiver.username} has invited you for a job position."
    msg = Message(
        sender_id=jobgiver.id, 
        receiver_id=candidate.id,  # This should ONLY be the candidate
        message=invite_message, 
        file_type='cv', 
        file_id=cv_id,
        message_type='invite'
    )
    db.session.add(msg)
    db.session.commit()

    # Notify candidate ONLY
    notify(candidate.id, "Interview Invite", f"{jobgiver.username} invited you", 'invite', msg.id)

    return jsonify({'success': 'Invite sent successfully!'})

# === DEBUG: Check messages in database ===
@app.route('/debug/messages')
def debug_messages():
    if 'username' not in session:
        return "Not logged in"
    
    user = User.query.filter_by(username=session['username']).first()
    all_messages = Message.query.all()
    
    debug_info = []
    for msg in all_messages:
        debug_info.append({
            'id': msg.id,
            'sender': msg.sender.username if msg.sender else 'None',
            'receiver': msg.receiver.username if msg.receiver else 'None', 
            'message': msg.message,
            'message_type': msg.message_type,
            'file_type': msg.file_type,
            'file_id': msg.file_id,
            'sent_at': msg.sent_at
        })
    
    return jsonify(debug_info)

# === DEBUG: Check applications ===
@app.route('/debug/applications')
def debug_applications():
    if 'username' not in session:
        return "Not logged in"
    
    all_apps = Application.query.all()
    
    debug_info = []
    for app in all_apps:
        debug_info.append({
            'id': app.id,
            'candidate': app.candidate.username if app.candidate else 'None',
            'job': app.job.filename if app.job else 'None',
            'job_owner': app.job.user.username if app.job and app.job.user else 'None',
            'applied_at': app.applied_at
        })
    
    return jsonify(debug_info)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('homepage'))

# =====================
# CAREER ROUTES BLUEPRINT
# =====================
# Import and register career routes at the END to avoid circular imports
from career_routes import career_bp
app.register_blueprint(career_bp)

# =====================
# ADMIN ROUTES
# =====================
from admin import admin_bp
app.register_blueprint(admin_bp)

# =====================
# RUN FLASK SERVER
# =====================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)