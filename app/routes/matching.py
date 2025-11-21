from flask import Blueprint, request, session, flash, redirect, url_for, render_template, current_app
from app import db
from app.models import User, CandidateCV, JobRequirement, Shortlist, SavedJob, Message
from ai_logic.vectorizer import get_embedding
from ai_logic.matcher import match_documents
from ai_logic.extract_text import extract_cv_text, extract_job_text, read_pdf_text
import os
import logging

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/match-candidates', methods=['POST'])
def match_candidates():
    if 'role' in session and session['role'] == 'jobgiver':
        job_id = request.form.get('job_id')
        if not job_id:
            flash("Job ID not provided.", "error")
            return redirect(url_for('jobgiver.jobgiver'))

        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            flash("Job not found.", "error")
            return redirect(url_for('jobgiver.jobgiver'))

        job_path = os.path.join(current_app.config['JOBGIVER_UPLOADS'], job.filename)
        if not os.path.exists(job_path):
            flash("Job file missing.", "error")
            return redirect(url_for('jobgiver.jobgiver'))

        try:
            raw_text = read_pdf_text(job_path)
            job_text = extract_job_text(raw_text)
            logging.debug(f"Extracted job text: {job_text[:200]}...")
            if not job_text.strip():
                flash("No relevant text extracted from job.", "error")
                return redirect(url_for('jobgiver.jobgiver'))
        except Exception as e:
            flash(f"Error extracting job text: {str(e)}", "error")
            return redirect(url_for('jobgiver.jobgiver'))

        cvs = CandidateCV.query.filter_by(domain=job.domain).all()
        cv_texts, cv_names = [], []
        for cv in cvs:
            path = os.path.join(current_app.config['CANDIDATE_UPLOADS'], cv.filename)
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
            flash("No CVs available for this domain.", "error")
            return redirect(url_for('jobgiver.jobgiver'))

        results = match_documents(job_text, cv_texts, cv_names, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        
        results = [(name, min(round(max(score, 0.0) * 100, 2), 100.0), job.domain) for name, score in results if score > 0.3]
        logging.debug(f"Final percentage scores: {[(name, score) for name, score, _ in results]}")

        matched_cvs = []
        for cv_file, score, domain in results:
            cv = CandidateCV.query.filter_by(filename=cv_file).first()
            matched_cvs.append((cv_file, score, domain, int(cv.id) if cv else 0))

        cv_ids = [c[3] for c in matched_cvs if c[3] is not None]
       
        shortlist_map = {s.cv_id: True for s in Shortlist.query.filter_by(jobgiver_id=user.id).all()}

        invite_map = {m.file_id: True for m in Message.query.filter_by(sender_id=user.id, message_type='invite').all()}

        return render_template(
            'match_results.html',
            results=matched_cvs,
            job_file=job.filename,
            cv_ids=cv_ids,
            shortlist_map=shortlist_map,
            invite_map=invite_map
        )

    return redirect(url_for('auth.login'))

@matching_bp.route('/match-jobs', methods=['POST'])
def match_jobs():
    if 'role' in session and session['role'] == 'candidate':
        user = User.query.filter_by(username=session['username']).first()
        cv_id = request.form.get('cv_id')
        if not cv_id:
            flash("CV ID not provided.", "error")
            return redirect(url_for('candidate.candidate'))

        cv = CandidateCV.query.filter_by(id=cv_id, user_id=user.id).first()
        if not cv:
            flash("CV not found.", "error")
            return redirect(url_for('candidate.candidate'))

        cv_path = os.path.join(current_app.config['CANDIDATE_UPLOADS'], cv.filename)
        if not os.path.exists(cv_path):
            flash("CV file missing.", "error")
            return redirect(url_for('candidate.candidate'))

        try:
            raw_text = read_pdf_text(cv_path)
            cv_text = extract_cv_text(raw_text)
            logging.debug(f"Extracted CV text: {cv_text[:200]}...")
            if not cv_text.strip():
                flash("No relevant text extracted from CV.", "error")
                return redirect(url_for('candidate.candidate'))
        except Exception as e:
            flash(f"Error extracting CV text: {str(e)}", "error")
            return redirect(url_for('candidate.candidate'))

        jobs = JobRequirement.query.filter_by(domain=cv.domain).all()
        job_texts, job_files = [], []
        for job in jobs:
            path = os.path.join(current_app.config['JOBGIVER_UPLOADS'], job.filename)
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
            flash("No jobs available for this domain.", "error")
            return redirect(url_for('candidate.candidate'))

        results = match_documents(cv_text, job_texts, job_files, get_embedding)
        logging.debug(f"Raw similarity scores before scaling: {[(name, score) for name, score in results]}")
        
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

    return redirect(url_for('auth.login'))