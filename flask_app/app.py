import sqlite3
from flask import Flask, request, redirect, render_template
from db_setup import create_tables

app = Flask(__name__)

create_tables()

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for the Recruiter Dashboard (index)
@app.route('/')
def index():
    conn = get_db_connection()
    jobs = conn.execute('SELECT job_id, job_title FROM Job_Listings').fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

# Route to add a job listing
@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        requirements = request.form['requirements']

        conn = get_db_connection()
        conn.execute('INSERT INTO Job_Listings (job_title, job_description, requirements) VALUES (?, ?, ?)',
                     (job_title, job_description, requirements))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add_job.html')

# Route to view applicants for a job
@app.route('/view_applicants/<int:job_id>')
def view_applicants(job_id):
    conn = get_db_connection()
    job = conn.execute('SELECT job_title FROM Job_Listings WHERE job_id = ?', (job_id,)).fetchone()
    applicants = conn.execute(''' 
        SELECT Candidates.name, Candidates.email, Applications.status
        FROM Applications
        JOIN Candidates ON Applications.candidate_id = Candidates.candidate_id
        WHERE Applications.job_id = ?
    ''', (job_id,)).fetchall()
    conn.close()
    return render_template('view_applicants.html', job=job, applicants=applicants)

# Route to render the resume submission form
@app.route("/upload_resume", methods=["GET"])
def upload_resume():
    return render_template("upload_resume.html")

# Route to handle resume submission and save data to the database
@app.route("/submit_resume", methods=["POST"])
def submit_resume():
    # Get form data
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    resume_content = request.form["resume_content"]
    
    # Insert candidate data into Candidates table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Candidates (name, email, phone) VALUES (?, ?, ?)",
        (name, email, phone)
    )
    candidate_id = cursor.lastrowid  # Get the ID of the newly inserted candidate
    
    # Insert resume content into Resumes table
    cursor.execute(
        "INSERT INTO Resumes (candidate_id, content) VALUES (?, ?)",
        (candidate_id, resume_content)
    )
    
    conn.commit()  # Commit the transaction
    conn.close()   # Close the connection

    return redirect("/")  # Redirect to the home page after successful submission

if __name__ == '__main__':
    app.run(debug=True)
