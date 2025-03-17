# Flask SQLite Demo

This is a simple Flask application that stores and retrieves names using SQLite.

## Installation

1. Clone the repository or create the files manually.
2. a) Install Flask:

   ```sh
   pip install flask
   ```
   OR
   
   b) Create and activate a Python virtual environment, then install the dependency file:

   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the Flask application:

   ```sh
   python app.py
   ```

4. Open your browser and go to:

   ```
   http://127.0.0.1:5000/
   ```

## Usage

- Enter a name in the form and submit it.
- The name will be stored in an SQLite database.
- Stored names will be displayed below the form.

## Exploring the Database

1. Open SQLite shell:

   ```sh
   sqlite3 database.db
   ```

2. View stored names:

   ```sql
   SELECT * FROM users;
   ```

3. Exit:

   ```sql
   .exit
   ```

## File Structure

```
/flask_sqlite_demo
│── app.py               # Flask application
│── database.db          # SQLite database (auto-created)
│── templates/
│   └── index.html       # HTML template
└── README.md            # This file
```

## License

This project is MIT licensed.

