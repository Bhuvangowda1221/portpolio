from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(256), nullable=True)
    link = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def save_image(file):
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            return filename
        except Exception as e:
            app.logger.error(f"Error saving image: {e}")
            return None
    return None

@app.route('/')
def home():
    try:
        projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    except Exception as e:
        app.logger.error(f"Error fetching projects for home: {e}")
        projects = []
    return render_template('home.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    except Exception as e:
        app.logger.error(f"Error fetching projects: {e}")
        projects = []
        flash('Error loading projects. Please try again later.', 'danger')
    return render_template('projects.html', projects=projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            
            if not all([name, email, message]):
                flash('All fields are required.', 'danger')
                return render_template('contact.html')
            
            app.logger.info(f"Contact from {name} <{email}>: {message}")
            flash('Message received! Thank you for contacting us.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            app.logger.error(f"Error processing contact form: {e}")
            flash('Error sending message. Please try again.', 'danger')
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            password = request.form.get('password', '')
            if password == app.config['ADMIN_PASSWORD']:
                session['admin_authenticated'] = True
                flash('Logged in successfully.', 'success')
                return redirect(url_for('admin_dashboard'))
            flash('Invalid password.', 'danger')
        except Exception as e:
            app.logger.error(f"Error during admin login: {e}")
            flash('Login error. Please try again.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    flash('Logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    except Exception as e:
        app.logger.error(f"Error fetching projects for admin: {e}")
        projects = []
        flash('Error loading projects. Please try again.', 'danger')
    return render_template('admin_dashboard.html', projects=projects)

@app.route('/admin/project/new', methods=['GET', 'POST'])
def new_project():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            link = request.form.get('link', '').strip() or None
            
            if not title or not description:
                flash('Title and description are required.', 'danger')
                return render_template('project_form.html', action='New', project=None)
            
            image = save_image(request.files.get('image'))
            project = Project(title=title, description=description, image=image, link=link)
            db.session.add(project)
            db.session.commit()
            flash('Project added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating project: {e}")
            flash('Error creating project. Please try again.', 'danger')
    return render_template('project_form.html', action='New', project=None)

@app.route('/admin/project/<int:pid>/edit', methods=['GET', 'POST'])
def edit_project(pid):
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    project = Project.query.get_or_404(pid)
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            link = request.form.get('link', '').strip() or None
            
            if not title or not description:
                flash('Title and description are required.', 'danger')
                return render_template('project_form.html', action='Edit', project=project)
            
            project.title = title
            project.description = description
            project.link = link
            
            img = request.files.get('image')
            if img and img.filename:
                new_image = save_image(img)
                if new_image:
                    project.image = new_image
            
            db.session.commit()
            flash('Project updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating project: {e}")
            flash('Error updating project. Please try again.', 'danger')
    return render_template('project_form.html', action='Edit', project=project)

@app.route('/admin/project/<int:pid>/delete', methods=['POST'])
def delete_project(pid):
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    try:
        project = Project.query.get_or_404(pid)
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting project: {e}")
        flash('Error deleting project. Please try again.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.cli.command('seed')
def seed():
    with app.app_context():
        db.create_all()
        if Project.query.count() == 0:
            projects = [
                Project(
                    title='Calculator App',
                    description='A fully functional calculator application built with Python and Tkinter. Features basic arithmetic operations with a clean, user-friendly interface.',
                    link='https://github.com/yourusername/calculator'
                ),
                Project(
                    title='Digital Clock',
                    description='An elegant digital clock application with customizable themes and time formats. Built using Python with a modern GUI interface.',
                    link='https://github.com/yourusername/clock'
                ),
                Project(
                    title='College Payment Website',
                    description='A comprehensive web application for managing college fee payments. Features student authentication, payment tracking, and admin dashboard.',
                    link='https://github.com/yourusername/college-payment'
                ),
                Project(
                    title='Personal Diary App',
                    description='A secure personal diary application with password protection, entry management, and search functionality. Built with Flask and SQLite.',
                    link='https://github.com/yourusername/diary-app'
                ),
                Project(
                    title='Tic Tac Toe Game',
                    description='Interactive Tic Tac Toe game with both single-player (vs AI) and multiplayer modes. Features a clean GUI and smart AI opponent.',
                    link='https://github.com/yourusername/tic-tac-toe'
                ),
                Project(
                    title='Multi-Game Platform',
                    description='A gaming platform featuring multiple classic games including Hand Cricket and Tic Tac Toe. Built with Python and modern game mechanics.',
                    link='https://github.com/yourusername/multi-games'
                )
            ]
            db.session.add_all(projects)
            db.session.commit()
            print(f'{len(projects)} sample projects added successfully.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
