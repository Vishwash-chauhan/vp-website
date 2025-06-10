from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', active_page='home')

@main.route('/experts')
def experts():
    return render_template('experts.html', active_page='experts')

@main.route('/club')
def club():
    return render_template('club.html', active_page='club')

@main.route('/about')
def about():
    return render_template('about.html', active_page='about')