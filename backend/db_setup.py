# CMON 20250303 CSCI 331 db_setup.py
# create and initalize the database
# run once to create database.db

import sqlite3

DB_FILE = "database.db"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
        """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database initialized. Have a nice day.")