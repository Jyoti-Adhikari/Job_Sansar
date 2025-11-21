from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for
from app import db
from app.models import User, Message, Application, Notification, Shortlist, SavedJob, CandidateCV, JobRequirement
from app.utils.helpers import notify

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/inbox')
def inbox():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    messages = Message.query.filter(
        Message.receiver_id == user.id
    ).order_by(Message.sent_at.desc()).all()
    
    unread_count = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    
    return render_template('inbox.html', messages=messages, unread_count=unread_count, current_user=user)

@messaging_bp.route('/inbox-data')
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

@messaging_bp.route('/mark-message-read', methods=['POST'])
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

@messaging_bp.route('/apply', methods=['POST'])
def apply_now():
    if session.get('role') != 'candidate':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    job_id = data.get('job_id')
    
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

    app = Application(candidate_id=user.id, job_id=job_id)
    db.session.add(app)
    
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
    
    db.session.commit()
    notify(job.user_id, "New Application", f"{user.username} applied to your job", 'application', app.id)

    return jsonify({'success': 'Applied successfully!'})

@messaging_bp.route('/send-invite', methods=['POST'])
def send_invite():
    if session.get('role') != 'jobgiver':
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    cv_id = data.get('cv_id')

    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400

    jobgiver = User.query.filter_by(username=session['username']).first()
    cv = CandidateCV.query.get(cv_id)
    
    if not cv:
        return jsonify({"error": "CV not found"}), 404
        
    candidate_user = cv.user

    existing_invite = Message.query.filter_by(
        sender_id=jobgiver.id, receiver_id=candidate_user.id, message_type='invite', file_id=cv_id
    ).first()
    if existing_invite:
        return jsonify({"error": "Invite already sent to this candidate"}), 400

    invite_message = f"{jobgiver.company_name or jobgiver.username} has invited you for a job position."
    msg = Message(
        sender_id=jobgiver.id, 
        receiver_id=candidate_user.id,
        message=invite_message, 
        file_type='cv', 
        file_id=cv_id,
        message_type='invite'
    )
    db.session.add(msg)
    db.session.commit()
    notify(candidate_user.id, "Interview Invite", f"{jobgiver.username} invited you", 'invite', msg.id)

    return jsonify({'success': 'Invite sent successfully!'})

@messaging_bp.route('/api/counts')
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