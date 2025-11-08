from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app import db, User, Feedback, CandidateCV, JobRequirement, UserSkills, Shortlist, SavedJob, Application, Message, Notification

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    users = User.query.all()
    jobs = JobRequirement.query.all()
    cvs = CandidateCV.query.all()
    return render_template('admin/dashboard.html', users=users, jobs=jobs, cvs=cvs)

@admin_bp.route('/admin/feedback', methods=['GET'])
def view_feedback():
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    feedback_list = Feedback.query.join(User).with_entities(
        Feedback.id, Feedback.message, Feedback.submitted_at, User.username
    ).order_by(Feedback.submitted_at.desc()).all()
    return render_template('admin/feedback.html', feedback_list=feedback_list)

@admin_bp.route('/admin/feedback/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted successfully!", "success")
    return redirect(url_for('admin.view_feedback'))

@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    
    # PREVENT ADMIN FROM DELETING THEMSELVES - FIXED
    current_user_id = session.get('user_id')
    if user.id == current_user_id:
        flash("You cannot delete your own account!", "error")
        return redirect(url_for('admin.admin_dashboard'))
    
    # ADDITIONAL PROTECTION: Prevent deletion of main admin account (jyoti)
    if user.username == 'jyoti' and user.role == 'admin':
        flash("The primary admin account cannot be deleted for system security.", "error")
        return redirect(url_for('admin.admin_dashboard'))
    
    # Delete all associated data to maintain referential integrity
    try:
        # Delete user skills
        UserSkills.query.filter_by(user_id=user_id).delete()
        
        # Delete candidate-related data
        CandidateCV.query.filter_by(user_id=user_id).delete()
        SavedJob.query.filter_by(candidate_id=user_id).delete()
        Application.query.filter_by(candidate_id=user_id).delete()
        
        # Delete jobgiver-related data  
        JobRequirement.query.filter_by(user_id=user_id).delete()
        Shortlist.query.filter_by(jobgiver_id=user_id).delete()
        
        # Delete messages and notifications
        Message.query.filter_by(sender_id=user_id).delete()
        Message.query.filter_by(receiver_id=user_id).delete()
        Notification.query.filter_by(user_id=user_id).delete()
        
        # Delete feedback
        Feedback.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' deleted successfully!", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/cv/delete/<int:cv_id>', methods=['POST'])
def delete_cv(cv_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    
    cv = CandidateCV.query.get_or_404(cv_id)
    
    # Also delete related shortlists
    Shortlist.query.filter_by(cv_id=cv_id).delete()
    
    db.session.delete(cv)
    db.session.commit()
    flash("Candidate CV deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/job/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    
    job = JobRequirement.query.get_or_404(job_id)
    
    # Also delete related applications and saved jobs
    Application.query.filter_by(job_id=job_id).delete()
    SavedJob.query.filter_by(job_id=job_id).delete()
    
    db.session.delete(job)
    db.session.commit()
    flash("Job requirement deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))