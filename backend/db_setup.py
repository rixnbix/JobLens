# CMON 20250303 CSCI 331 db_setup.py
# create and initalize the database
# run once to create database.db

import sqlite3

DB_FILE = "database.db"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # note: each query here needs its own `cursor.execute()` 
    # for single-line, a single pair of enclosing double quotation marks is fine
    # for multi-line, triplets of double quotation marks is required

    # turn on SQLite FK constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # note: SQLite doesn't really support adding/removing constraints after building the db like this
    # so we gotta be sure our FK/PK and any CHECK constraints (if we end up using them) are in from the get
    # otherwise, we need to DROP and re-CREATE (so, it's possible to fix this, just a pita)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employers (
            employer_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Job_Listings (
            job_id INTEGER PRIMARY KEY,
            employer_id INTEGER,
            job_title TEXT NOT NULL,
            job_description TEXT,
            requirements TEXT,
            FOREIGN KEY (employer_id) REFERENCES Employers(employer_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Candidates (
            candidate_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Resumes (
            resume_id INTEGER PRIMARY KEY,
            candidate_id INTEGER,
            content TEXT,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY,
            job_id INTEGER,
            candidate_id INTEGER,
            resume_id INTEGER,
            status TEXT,
            FOREIGN KEY (job_id) REFERENCES Job_Listings(job_id),
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id),
            FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Keywords (
            keyword_id INTEGER PRIMARY KEY,
            job_id INTEGER,
            keyword TEXT,
            FOREIGN KEY (job_id) REFERENCES Job_Listings(job_id)
        );
    """)

    # note: SQLite uses `REAL` for floats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Match_Scores (
            match_id INTEGER PRIMARY KEY,
            application_id INTEGER,
            score REAL,
            FOREIGN KEY (application_id) REFERENCES Applications(application_id)
        );
    """)

    conn.commit()
    conn.close()

# note: basic command-line test for table existence: `sqlite3 database.db ".tables"`
if __name__ == "__main__":
    create_tables()
    print("Database initialized. Have a nice day.")