import sqlite3
import re
import nltk
from flask import Flask, request, redirect, render_template
from db_setup import create_tables
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from pattern_matcher import PatternMatcher
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download("stopwords")

app = Flask(__name__)

create_tables()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    jobs = conn.execute('SELECT job_id, job_title, job_description, requirements FROM Job_Listings').fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

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

@app.route('/view_applicants/<int:job_id>')
def view_applicants(job_id):
    conn = get_db_connection()
    job = conn.execute('SELECT job_title, requirements FROM Job_Listings WHERE job_id = ?', (job_id,)).fetchone()

    rows = conn.execute('''
        SELECT C.candidate_id, C.name, C.email, A.status, R.content AS resume
        FROM Applications A
        JOIN Candidates C ON A.candidate_id = C.candidate_id
        JOIN Resumes R ON C.candidate_id = R.candidate_id
        WHERE A.job_id = ?
    ''', (job_id,)).fetchall()
    conn.close()

    # Build a pattern string from the job requirements
    patterns = re.findall(r"\b[a-zA-Z]{2,}\b", job['requirements'].lower())
    pm = PatternMatcher(patterns)

    applicants = []
    for row in rows:
        matches = pm.search(row['resume'].lower())
        matched = {kw for _, kw in matches}
        score = round((len(matched) / len(patterns) * 100), 2) if patterns else 0 # Percentage match
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
def apply_job(job_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        resume_content = request.form['resume_content']

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
        resume_id = cursor.lastrowid  # Get the ID of the inserted resume

        # Insert application into Applications table
        cursor.execute(
            "INSERT INTO Applications (job_id, candidate_id, resume_id, status) VALUES (?, ?, ?, ?)",
            (job_id, candidate_id, resume_id, 'Pending')
        )

        conn.commit()  # Commit the transaction
        conn.close()  # Close the connection

        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the job details
    cursor.execute("SELECT * FROM Job_Listings WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    return render_template('apply_job.html', job=job, job_id=job_id)



# # Function to extract keywords using TF-IDF
# def extract_keywords(text, num_keywords=10):
#     text = re.sub(r"[^a-zA-Z\s]", "", text)
#     words = word_tokenize(text.lower())
#     words = [word for word in words if word not in stopwords.words("english")]

#     vectorizer = TfidfVectorizer(stop_words="english", max_features=num_keywords)
#     vectors = vectorizer.fit_transform([" ".join(words)])
#     keywords = vectorizer.get_feature_names_out()

#     return list(keywords)

# # Function to match resume keywords with job requirements
# def match_keywords(resume_keywords, job_description):
#     job_keywords = extract_keywords(job_description)
#     matched_keywords = set(resume_keywords) & set(job_keywords)  # Find common words
#     match_score = len(matched_keywords) / len(job_keywords) * 100  # Percentage match
#     return matched_keywords, round(match_score, 2)

# @app.route("/match/<int:job_id>/<int:candidate_id>")
# def match_resume(job_id, candidate_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Get resume content
#     cursor.execute("SELECT content FROM Resumes WHERE candidate_id=?", (candidate_id,))
#     resume_content = cursor.fetchone()[0]

#     # Get job requirements
#     cursor.execute("SELECT requirements FROM Job_Listings WHERE job_id=?", (job_id,))
#     job_requirements = cursor.fetchone()[0]

#     conn.close()

#     # Build Aho–Corasick automaton from job requirements
#     import re
#     from aho import PatternMatcher

#     patterns = re.findall(r"\b[a-zA-Z]{2,}\b", job_requirements.lower())
#     pm = PatternMatcher(patterns)
#     matches = pm.search(resume_content.lower())

#     matched_keywords = {pattern for _, pattern in matches}
#     score = round(len(matched_keywords) / len(patterns) * 100, 2) if patterns else 0

#     return render_template("match_result.html", matched_keywords=matched_keywords, score=score)

@app.route("/submit_resume", methods=["POST"])
def submit_resume():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    resume_content = request.form["resume_content"]
    
    keywords = extract_keywords(resume_content)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Candidates (name, email, phone) VALUES (?, ?, ?)",
        (name, email, phone)
    )
    candidate_id = cursor.lastrowid
    
    cursor.execute(
        "INSERT INTO Resumes (candidate_id, content) VALUES (?, ?)",
        (candidate_id, resume_content)
    )
    resume_id = cursor.lastrowid

    for keyword in keywords:
        cursor.execute(
            "INSERT INTO Keywords (job_id, keyword) VALUES (?, ?)",
            (resume_id, keyword),
        )

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
