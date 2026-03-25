from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@views_bp.route('/coach')
def coach():
    return render_template('coach.html')

@views_bp.route('/market')
def market():
    return render_template('market.html')
