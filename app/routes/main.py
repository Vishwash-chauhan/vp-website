from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash
from app.models import Expert, User, Category
from app import db
from app.forms.expert import ExpertForm
import base64

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get featured experts first
    featured_experts = Expert.get_featured()
    
    # If no featured experts, get verified experts as fallback
    if not featured_experts:
        featured_experts = Expert.get_verified()[:3]
    
    # If still no experts, get first 3 available experts
    if not featured_experts:
        featured_experts = Expert.get_all_available()[:3]
    
    # Get 6 active categories for the popular categories section
    popular_categories = Category.query.filter(Category.is_active == True).limit(6).all()
    
    return render_template('index.html', active_page='home', experts=featured_experts, categories=popular_categories)

@main.route('/experts')
def experts():
    # Get all available experts with categories
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    query = Expert.query.filter(Expert.is_available == True)
    
    # Filter by category if specified
    if category_id:
        query = query.join(Expert.categories).filter(Category.id == category_id)
    
    all_experts = query.all()
    categories = Category.query.filter(Category.is_active == True).all()
    
    return render_template('experts.html', active_page='experts', experts=all_experts, categories=categories)

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
def dashboard():
    """Dashboard - now accessible to all users"""
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
def dashboard_users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('dashboard_users.html', active_page='dashboard', users=users)

@main.route('/dashboard/experts')
def dashboard_experts():
    """Expert management page"""
    page = request.args.get('page', 1, type=int)
    experts = Expert.query.paginate(page=page, per_page=10, error_out=False)
    featured_count = Expert.get_featured_count()
    return render_template('dashboard_experts.html', active_page='dashboard', experts=experts, featured_count=featured_count)

@main.route('/dashboard/user/<int:user_id>/delete', methods=['POST'])
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

@main.route('/dashboard/expert/<int:expert_id>/toggle-featured', methods=['POST'])
def toggle_expert_featured(expert_id):
    """Toggle expert featured status"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        if expert.is_featured:
            expert.unset_featured()
            flash(f'Expert {expert.name} is no longer featured.', 'success')
        else:
            featured_count = Expert.get_featured_count()
            if featured_count >= 3:
                flash('Maximum 3 experts can be featured. Please unfeature another expert first.', 'error')
            else:
                if expert.set_featured():
                    flash(f'Expert {expert.name} is now featured at position {expert.featured_position}.', 'success')
                else:
                    flash('Error setting expert as featured.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expert featured status: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/user/<int:user_id>/toggle-admin', methods=['POST'])
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
def add_expert():
    """Add new expert"""
    form = ExpertForm()
    
    # Populate categories choices
    categories = Category.query.filter(Category.is_active == True).all()
    form.categories.choices = [(c.id, c.name) for c in categories]
    
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
            
            # Add selected categories
            selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
            expert.categories = selected_categories
            
            db.session.add(expert)
            db.session.commit()
            flash(f'Expert {expert.name} has been added successfully!', 'success')
            return redirect(url_for('main.dashboard_experts'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding expert: {str(e)}', 'error')
    
    return render_template('expert_form.html', form=form, title='Add New Expert', action='Add')

@main.route('/dashboard/expert/<int:expert_id>/edit', methods=['GET', 'POST'])
def edit_expert(expert_id):
    """Edit expert profile"""
    expert = Expert.query.get_or_404(expert_id)
    form = ExpertForm(obj=expert)
    
    # Populate categories choices
    categories = Category.query.filter(Category.is_active == True).all()
    form.categories.choices = [(c.id, c.name) for c in categories]
    
    # Pre-select expert's current categories
    if request.method == 'GET':
        form.categories.data = [c.id for c in expert.categories]
    
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
            
            # Update categories
            selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
            expert.categories = selected_categories
            
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

# Category Management Routes

@main.route('/dashboard/categories')
def dashboard_categories():
    """Categories management page"""
    categories = Category.query.order_by(Category.created_at.desc()).all()
    active_count = Category.query.filter(Category.is_active == True).count()
    
    # Count experts with categories
    expert_count = db.session.query(Expert.id).join(Expert.categories).distinct().count()
    
    return render_template('dashboard_categories.html', 
                         active_page='dashboard',
                         categories=categories,
                         active_count=active_count,
                         expert_count=expert_count)

@main.route('/dashboard/category/add', methods=['GET', 'POST'])
def add_category():
    """Add a new category - separate page"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_active = 'is_active' in request.form
            
            if not name:
                flash('Category name is required.', 'error')
                return render_template('add_category.html', active_page='dashboard')
            
            if not description:
                flash('Category description is required.', 'error')
                return render_template('add_category.html', active_page='dashboard')
            
            # Check if category name already exists
            if Category.query.filter(Category.name.ilike(name)).first():
                flash('A category with this name already exists.', 'error')
                return render_template('add_category.html', active_page='dashboard')
            
            category = Category(
                name=name,
                description=description,
                is_active=is_active
            )
            
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{name}" has been added successfully!', 'success')
            return redirect(url_for('main.dashboard_categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding category: {str(e)}', 'error')
            return render_template('add_category.html', active_page='dashboard')
    
    return render_template('add_category.html', active_page='dashboard')

@main.route('/dashboard/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    """Edit an existing category - separate page"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_active = 'is_active' in request.form
            
            if not name:
                flash('Category name is required.', 'error')
                return render_template('edit_category.html', category=category, active_page='dashboard')
            
            if not description:
                flash('Category description is required.', 'error')
                return render_template('edit_category.html', category=category, active_page='dashboard')
            
            # Check if category name already exists (excluding current category)
            existing = Category.query.filter(Category.name.ilike(name), Category.id != category_id).first()
            if existing:
                flash('A category with this name already exists.', 'error')
                return render_template('edit_category.html', category=category, active_page='dashboard')
            
            category.name = name
            category.description = description
            category.is_active = is_active
            
            db.session.commit()
            flash(f'Category "{name}" has been updated successfully!', 'success')
            return redirect(url_for('main.dashboard_categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'error')
            return render_template('edit_category.html', category=category, active_page='dashboard')
    
    return render_template('edit_category.html', category=category, active_page='dashboard')

@main.route('/dashboard/category/toggle', methods=['POST'])
def toggle_category():
    """Toggle category active status"""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        is_active = data.get('is_active')
        
        category = Category.query.get_or_404(category_id)
        category.is_active = is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Category "{category.name}" has been {"activated" if is_active else "deactivated"}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main.route('/dashboard/category/delete', methods=['POST'])
def delete_category():
    """Delete a category (only if no experts are assigned)"""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        
        category = Category.query.get_or_404(category_id)
        
        # Check if any experts are assigned to this category
        if category.experts:
            return jsonify({
                'success': False,
                'message': f'Cannot delete category "{category.name}" because it has {len(category.experts)} expert(s) assigned to it.'
            }), 400
        
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Category "{category_name}" has been deleted successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500