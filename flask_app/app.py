import sqlite3
import re
import nltk
from flask import Flask, request, redirect, render_template, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from db_setup import create_tables
from pattern_matcher import PatternMatcher

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download("stopwords")

app = Flask(__name__)
app.secret_key = 'f9b5e2c8d4a7b9f1e3c2d5a8b6f9e1c4d7a2b5f8e9c1d3'  # For testing only

# Initialize Flask-Login and Bcrypt
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

create_tables()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = f"{role}_{id}"  # e.g., "candidate_1" or "employer_1"
        self.email = email
        self.role = role

    def get_id(self):
        return self.id  # Flask-Login uses this to store in session

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    role, id = user_id.split('_', 1)
    id = int(id)
    if role == 'employer':
        employer = conn.execute('SELECT * FROM Employers WHERE employer_id = ?', (id,)).fetchone()
        if employer:
            conn.close()
            print(f"load_user: Employer {employer['email']}, role: employer")
            return User(employer['employer_id'], employer['email'], 'employer')
    elif role == 'candidate':
        candidate = conn.execute('SELECT * FROM Candidates WHERE candidate_id = ?', (id,)).fetchone()
        if candidate:
            conn.close()
            print(f"load_user: Candidate {candidate['email']}, role: candidate")
            return User(candidate['candidate_id'], candidate['email'], 'candidate')
    conn.close()
    return None

@app.route('/register_candidate', methods=['GET', 'POST'])
def register_candidate():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Candidates (name, email, phone, password) VALUES (?, ?, ?, ?)',
                         (name, email, phone, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.')
        finally:
            conn.close()
    return render_template('register_candidate.html')

@app.route('/register_employer', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        company_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Employers (company_name, email, password) VALUES (?, ?, ?)',
                         (company_name, email, hashed_password))
            conn.commit()
            flash('Employer registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.')
        finally:
            conn.close()
    return render_template('register_employer.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logout_user()  # Clear any existing session
        email = request.form['email']
        password = request.form['password']
        print(f"Login attempt with email: {email}")
        conn = get_db_connection()
        
        employer = conn.execute('SELECT * FROM Employers WHERE email = ?', (email,)).fetchone()
        print(f"Employer found: {employer}")
        if employer and bcrypt.check_password_hash(employer['password'], password):
            user = User(employer['employer_id'], employer['email'], 'employer')
            login_user(user)
            print(f"Logged in as employer: {user.email}, role: {user.role}, id: {user.id}")
            return redirect(url_for('admin_dashboard'))
        
        candidate = conn.execute('SELECT * FROM Candidates WHERE email = ?', (email,)).fetchone()
        print(f"Candidate found: {candidate}")
        if candidate and bcrypt.check_password_hash(candidate['password'], password):
            user = User(candidate['candidate_id'], candidate['email'], 'candidate')
            login_user(user)
            print(f"Logged in as candidate: {user.email}, role: {user.role}, id: {user.id}")
            return redirect(url_for('index'))
        
        flash('Invalid email or password.')
        print("Login failed: Invalid email or password")
        conn.close()
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    print(f"Index - Current user: {current_user.email if current_user.is_authenticated else 'None'}, role: {current_user.role if current_user.is_authenticated else 'None'}")
    conn = get_db_connection()
    jobs = conn.execute('SELECT job_id, job_title, job_description, requirements, employer_id FROM Job_Listings').fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    print(f"Admin Dashboard - Current user: {current_user.email}, role: {current_user.role}")
    if current_user.role != 'employer':
        flash('Access denied: Employers only.')
        return redirect(url_for('index'))
    conn = get_db_connection()
    raw_employer_id = int(current_user.id.split('_')[1])  # Extract "1" from "employer_1"
    jobs = conn.execute('SELECT job_id, job_title FROM Job_Listings WHERE employer_id = ?', (raw_employer_id,)).fetchall()
    print(f"Jobs found for employer_id={raw_employer_id}: {len(jobs)}")
    conn.close()
    return render_template('admin_dashboard.html', jobs=jobs)

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if current_user.role != 'employer':
        flash('Access denied: Employers only.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        requirements = request.form['requirements']

        conn = get_db_connection()
        raw_employer_id = int(current_user.id.split('_')[1])  # Extract "1" from "employer_1"
        conn.execute('INSERT INTO Job_Listings (employer_id, job_title, job_description, requirements) VALUES (?, ?, ?, ?)',
                     (raw_employer_id, job_title, job_description, requirements))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_job.html')

@app.route('/view_applicants/<int:job_id>')
@login_required
def view_applicants(job_id):
    if current_user.role != 'employer':
        flash('Access denied: Employers only.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    raw_employer_id = int(current_user.id.split('_')[1])  # Extract "1" from "employer_1"
    job = conn.execute('SELECT job_title, requirements FROM Job_Listings WHERE job_id = ? AND employer_id = ?', 
                       (job_id, raw_employer_id)).fetchone()
    print(f"Job found: {job}, employer_id: {current_user.id}")
    
    if not job:
        conn.close()
        flash('Job not found or you do not have permission.')
        return redirect(url_for('admin_dashboard'))

    # Only proceed if job is found and belongs to the employer
    rows = conn.execute('''
        SELECT C.candidate_id, C.name, C.email, A.status, R.content AS resume
        FROM Applications A
        JOIN Candidates C ON CAST(A.candidate_id AS INTEGER) = C.candidate_id
        JOIN Resumes R ON C.candidate_id = R.candidate_id
        WHERE A.job_id = ?
    ''', (job_id,)).fetchall()
    print(f"Applicants found: {len(rows)} for job_id: {job_id}")

    conn.close()

    patterns = re.findall(r"\b[a-zA-Z]{2,}\b", job['requirements'].lower())
    pm = PatternMatcher(patterns)

    applicants = []
    for row in rows:
        matches = pm.search(row['resume'].lower())
        matched = {kw for _, kw in matches}
        score = round((len(matched) / len(patterns) * 100), 2) if patterns else 0
        applicants.append({
            'candidate_id': row['candidate_id'],
            'name': row['name'],
            'email': row['email'],
            'status': row['status'],
            'keywords': sorted(matched),
            'score': score
        })

    return render_template('view_applicants.html', job=job, applicants=applicants)

@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'candidate':
        flash('Access denied: Candidates only.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        resume_content = request.form['resume_content']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            raw_candidate_id = int(current_user.id.split('_')[1])  # Extract "1" from "candidate_1"
            cursor.execute('UPDATE Candidates SET name = ?, phone = ? WHERE candidate_id = ?', 
                           (name, phone, raw_candidate_id))
            print(f"Updated candidate: {raw_candidate_id}, {name}, {phone}")

            cursor.execute('INSERT INTO Resumes (candidate_id, content) VALUES (?, ?)', 
                           (raw_candidate_id, resume_content))
            resume_id = cursor.lastrowid
            print(f"Inserted resume: resume_id={resume_id}, candidate_id={raw_candidate_id}")

            cursor.execute('INSERT INTO Applications (job_id, candidate_id, resume_id, status) VALUES (?, ?, ?, ?)', 
                           (job_id, raw_candidate_id, resume_id, 'Pending'))
            application_id = cursor.lastrowid
            print(f"Inserted application: application_id={application_id}, job_id={job_id}, candidate_id={raw_candidate_id}")

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            flash('Failed to apply to job. Please try again.')
        finally:
            conn.close()
        return redirect(url_for('index'))

    conn = get_db_connection()
    job = conn.execute('SELECT * FROM Job_Listings WHERE job_id = ?', (job_id,)).fetchone()
    conn.close()
    return render_template('apply_job.html', job=job, job_id=job_id)

if __name__ == '__main__':
    app.run(debug=True)