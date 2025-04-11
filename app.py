from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import secrets
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

app.secret_key = secrets.token_hex(32)

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), unique=True, nullable=False)
    Image = db.Column(db.String(10000))
    Description = db.Column(db.String(120), unique=True, nullable=False)
    cms_link = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Project {self.Name}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']

        image_data = image.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        mime_type = image.mimetype  # e.g., 'image/jpeg'
        image_src = f"data:{mime_type};base64,{image_base64}"

        new_project = Projects(
            Name=name,
            Image=image_src,
            Description=description,
            cms_link='dummy-link'
        )

        db.session.add(new_project)
        db.session.commit()

        flash('Project created successfully with base64 image!')
        return redirect('/create-project')
    else:
        return render_template('Create_Project.html')

@app.route('/view-projects')
def view_projects():
    projects = Projects.query.all()
    return render_template('View_Projects.html', projects=projects)

@app.route('/update-project/<int:id>', methods=['POST'])
def update_project_post(id):
    project = Projects.query.get_or_404(id)
    project.Name = request.form['name']
    project.Description = request.form['description']
    db.session.commit()
    flash('Project updated successfully!')
    return redirect(url_for('view_projects'))

@app.route('/delete-project/<int:id>')
def delete_project(id):
    project = Projects.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!')
    return redirect(url_for('view_projects'))

@app.route('/<name>')
def open_CMS(name):
    project = Projects.query.filter_by(Name=name).first()
    if project:
        return render_template('project.html', project=project)
    else:
        return "Project not found", 404

@app.route('/get_projects', methods=['GET'])
def get_projects():
    projects = Projects.query.all()
    
    if projects:
        project_list = [
            {
                "id": project.id,
                "name": project.Name,
                "description": project.Description,
                "image": project.Image
            }
            for project in projects
        ]
        return jsonify(project_list), 200
    else:
        return jsonify({"error": "No projects found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
