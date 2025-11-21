from flask import url_for
from app.models import CandidateCV, JobRequirement, Message, User
from app import db

def get_cv_filename(cv_id):
    cv = CandidateCV.query.get(cv_id)
    return cv.filename if cv else "unknown.pdf"

def get_job_filename(job_id):
    job = JobRequirement.query.get(job_id)
    return job.filename if job else "unknown.pdf"

def get_filename_from_message(message):
    if message.message_type == 'application':
        if message.file_type == 'job':
            job = JobRequirement.query.get(message.file_id)
            return job.filename if job else "unknown.pdf"
    elif message.message_type == 'invite':
        if message.file_type == 'cv':
            cv = CandidateCV.query.get(message.file_id)
            return cv.filename if cv else "unknown.pdf"
    return "unknown.pdf"

def get_file_url_from_message(message):
    filename = get_filename_from_message(message)
    if message.message_type == 'application' and message.file_type == 'job':
        return url_for('main.uploaded_job', filename=filename)
    elif message.message_type == 'invite' and message.file_type == 'cv':
        return url_for('main.uploaded_cv', filename=filename)
    elif message.file_type == 'cv':
        return url_for('main.uploaded_cv', filename=filename)
    elif message.file_type == 'job':
        return url_for('main.uploaded_job', filename=filename)
    return "#"

def get_sender_cv_filename(sender_id):
    sender = User.query.get(sender_id)
    if sender and sender.cvs:
        return sender.cvs[0].filename
    return "unknown.pdf"

def get_sender_job_filename(sender_id):
    sender = User.query.get(sender_id)
    if sender and sender.job_requirements:
        return sender.job_requirements[0].filename
    return "unknown.pdf"

def notify(user_id, title, body, type_, related_id):
    from app.models import Notification
    n = Notification(user_id=user_id, title=title, body=body, type=type_, related_id=related_id)
    db.session.add(n)
    db.session.commit()

def utility_processor():
    return dict(
        get_cv_filename=get_cv_filename,
        get_job_filename=get_job_filename,
        get_filename_from_message=get_filename_from_message,
        get_file_url_from_message=get_file_url_from_message,
        get_sender_cv_filename=get_sender_cv_filename,
        get_sender_job_filename=get_sender_job_filename
    )