from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, current_app
from app import db
from app.models import User, CandidateCV, JobRequirement, SavedJob, Message
from werkzeug.utils import secure_filename
import os

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/precandidate', methods=['GET', 'POST'])
def precandidate():
    jobs = JobRequirement.query.all()

    if request.method == 'POST':
        file = request.files.get('cv_file')
        domain = request.form.get('domain')

        if not file:
            flash("Please select a CV file.", "error")
            return redirect(url_for('candidate.precandidate'))

        if not file.filename.lower().endswith('.pdf'):
            flash("Only PDF files are allowed!", "error")
            return redirect(url_for('candidate.precandidate'))

        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['CANDIDATE_UPLOADS'], filename)
        file.save(save_path)

        flash("CV uploaded successfully!", "success")
        return redirect(url_for('candidate.precandidate'))

    return render_template('precandidate.html', jobs=jobs)

@candidate_bp.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        jobs = JobRequirement.query.all()

        if request.method == 'POST':
            file = request.files['cv_file']
            domain = request.form.get('domain')
            if file:
                filename = secure_filename(file.filename)
                if not filename.lower().endswith('.pdf'):
                    flash("Only PDFs allowed!", "error")
                    return redirect(url_for('candidate.candidate'))

                path = os.path.join(current_app.config['CANDIDATE_UPLOADS'], filename)
                file.save(path)

                new_cv = CandidateCV(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_cv)
                db.session.commit()

                flash("CV uploaded!", "success")

        cvs = CandidateCV.query.filter_by(user_id=user.id).all()
        return render_template(
            'candidate.html',
            cvs=cvs,
            username=user.username,
            jobs=jobs
        )
    return redirect(url_for('auth.login'))

@candidate_bp.route('/candidate/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if cv:
            path = os.path.join(current_app.config['CANDIDATE_UPLOADS'], cv.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(cv)
            db.session.commit()
            flash("CV deleted successfully!", "success")
        else:
            flash("CV not found!", "error")
    return redirect(url_for('candidate.candidate'))

@candidate_bp.route('/save-job', methods=['POST'])
def save_job():
    if session.get('role') != 'candidate': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    job_id = data.get('job_id')
    
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

@candidate_bp.route('/remove-saved-job', methods=['POST'])
def remove_saved_job():
    if session.get('role') != 'candidate': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    job_id = data.get('job_id')
    
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

@candidate_bp.route('/saved-jobs')
def saved_jobs():
    if session.get('role') != 'candidate': 
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['username']).first()
    saved_jobs = SavedJob.query.filter_by(candidate_id=user.id).all()
    
    items = []
    for saved in saved_jobs:
        job = JobRequirement.query.get(saved.job_id)
        if job:
            job_user = User.query.get(job.user_id)
            items.append((saved, job, job_user))
    
    return render_template('saved_jobs.html', items=items)