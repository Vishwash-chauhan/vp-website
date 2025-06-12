from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models import Expert, User
from app import db
from app.forms.expert import ExpertForm
import base64

main = Blueprint('main', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    # Get verified experts (as featured experts)
    featured_experts = Expert.get_verified()[:3]
    
    # If no verified experts, get first 3 available experts
    if not featured_experts:
        featured_experts = Expert.get_all_available()[:3]
    
    return render_template('index.html', active_page='home', experts=featured_experts)

@main.route('/experts')
def experts():
    # Get all available experts
    all_experts = Expert.get_all_available()
    return render_template('experts.html', active_page='experts', experts=all_experts)

@main.route('/expert/<int:expert_id>')
def expert_detail(expert_id):
    """Expert detail page"""
    expert = Expert.query.get_or_404(expert_id)
    
    # Get related experts (same expertise area, excluding current expert)
    related_experts = Expert.query.filter(
        Expert.expertise.contains(expert.expertise.split()[0]),  # First word of expertise
        Expert.id != expert_id,
        Expert.is_available == True
    ).limit(3).all()
    
    # If no related experts, get random available experts
    if not related_experts:
        related_experts = Expert.query.filter(
            Expert.id != expert_id,
            Expert.is_available == True
        ).limit(3).all()
    
    return render_template('expert_detail.html', active_page='experts', expert=expert, related_experts=related_experts)

@main.route('/api/experts/search')
def search_experts():
    """API endpoint for searching experts"""
    search_term = request.args.get('q', '')
    expertise = request.args.get('expertise', '')
    
    if search_term:
        experts = Expert.search_experts(search_term)
    elif expertise:
        experts = Expert.get_by_expertise(expertise)
    else:
        experts = Expert.get_all_available()
    
    return jsonify([expert.to_dict() for expert in experts])

@main.route('/club')
def club():
    return render_template('club.html', active_page='club')

@main.route('/about')
def about():
    return render_template('about.html', active_page='about')

@main.route('/dashboard')
@admin_required
def dashboard():
    """Admin Dashboard with CRUD operations for Users and Experts"""
    # Get statistics
    total_users = User.query.count()
    total_experts = Expert.query.count()
    active_experts = Expert.query.filter_by(is_available=True).count()
    verified_experts = Expert.query.filter_by(is_verified=True).count()
    
    # Get recent users and experts for display
    recent_users = User.query.order_by(User.date_created.desc()).limit(5).all()
    recent_experts = Expert.query.order_by(Expert.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         active_page='dashboard',
                         total_users=total_users,
                         total_experts=total_experts,
                         active_experts=active_experts,
                         verified_experts=verified_experts,
                         recent_users=recent_users,
                         recent_experts=recent_experts)

@main.route('/dashboard/users')
@admin_required
def dashboard_users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('dashboard_users.html', active_page='dashboard', users=users)

@main.route('/dashboard/experts')
@admin_required  
def dashboard_experts():
    """Expert management page"""
    page = request.args.get('page', 1, type=int)
    experts = Expert.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('dashboard_experts.html', active_page='dashboard', experts=experts)

@main.route('/dashboard/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_users'))

@main.route('/dashboard/expert/<int:expert_id>/delete', methods=['POST'])
@admin_required
def delete_expert(expert_id):
    """Delete an expert"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        db.session.delete(expert)
        db.session.commit()
        flash(f'Expert {expert.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting expert: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/expert/<int:expert_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_expert_status(expert_id):
    """Toggle expert availability status"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        expert.is_available = not expert.is_available
        db.session.commit()
        status = "available" if expert.is_available else "unavailable"
        flash(f'Expert {expert.name} is now {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expert status: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/expert/<int:expert_id>/toggle-verification', methods=['POST'])
@admin_required
def toggle_expert_verification(expert_id):
    """Toggle expert verification status"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        expert.is_verified = not expert.is_verified
        db.session.commit()
        status = "verified" if expert.is_verified else "unverified"
        flash(f'Expert {expert.name} is now {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expert verification: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = "admin" if user.is_admin else "regular user"
        flash(f'User {user.name} is now a {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user admin status: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_users'))

@main.route('/dashboard/expert/add', methods=['GET', 'POST'])
@admin_required
def add_expert():
    """Add new expert"""
    form = ExpertForm()
    if form.validate_on_submit():
        try:
            # Handle profile picture upload
            profile_picture_data = None
            if form.profile_picture.data:
                profile_picture_data = form.profile_picture.data.read()
            
            # Create new expert
            expert = Expert(
                name=form.name.data,
                expertise=form.expertise.data,
                bio=form.bio.data,
                about=form.about.data,
                contact=form.contact.data,
                phone_number=form.phone_number.data,
                portfolio_link=form.portfolio_link.data,
                linkedin_profile=form.linkedin_profile.data,
                twitter_profile=form.twitter_profile.data,
                instagram_profile=form.instagram_profile.data,
                hourly_rate=form.hourly_rate.data or 0.00,
                rating=form.rating.data or 5.00,
                reviews_count=form.reviews_count.data or 0,
                is_available=form.is_available.data,
                is_verified=form.is_verified.data,
                profile_picture=profile_picture_data
            )
            
            db.session.add(expert)
            db.session.commit()
            flash(f'Expert {expert.name} has been added successfully!', 'success')
            return redirect(url_for('main.dashboard_experts'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding expert: {str(e)}', 'error')
    
    return render_template('expert_form.html', form=form, title='Add New Expert', action='Add')

@main.route('/dashboard/expert/<int:expert_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_expert(expert_id):
    """Edit expert profile"""
    expert = Expert.query.get_or_404(expert_id)
    form = ExpertForm(obj=expert)
    
    if form.validate_on_submit():
        try:
            # Update expert fields
            expert.name = form.name.data
            expert.expertise = form.expertise.data
            expert.bio = form.bio.data
            expert.about = form.about.data
            expert.contact = form.contact.data
            expert.phone_number = form.phone_number.data
            expert.portfolio_link = form.portfolio_link.data
            expert.linkedin_profile = form.linkedin_profile.data
            expert.twitter_profile = form.twitter_profile.data
            expert.instagram_profile = form.instagram_profile.data
            expert.hourly_rate = form.hourly_rate.data or 0.00
            expert.rating = form.rating.data or 5.00
            expert.reviews_count = form.reviews_count.data or 0
            expert.is_available = form.is_available.data
            expert.is_verified = form.is_verified.data
              # Handle profile picture upload
            if form.profile_picture.data and hasattr(form.profile_picture.data, 'read'):
                expert.profile_picture = form.profile_picture.data.read()
            
            db.session.commit()
            flash(f'Expert {expert.name} has been updated successfully!', 'success')
            return redirect(url_for('main.dashboard_experts'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating expert: {str(e)}', 'error')
    
    return render_template('expert_form.html', form=form, expert=expert, title='Edit Expert', action='Update')