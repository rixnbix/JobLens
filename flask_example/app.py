from flask import Flask, request, redirect, render_template
import sqlite3

# Initialize the Flask web application
app = Flask(__name__)

# Function to initialize the database and create a table if it doesn't exist
def init_db():
    # Connect to the SQLite database file (creates it if not existing)
    with sqlite3.connect("database.db") as conn:
        # Execute an SQL command to create the "users" table if it does not exist
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        # Commit changes to make sure the table is created
        conn.commit()

# Call the function to initialize the database
init_db()

# Define the main route that renders the index page and fetches stored names
@app.route("/")
def index():
    # Connect to the database to fetch stored names
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()  # Create a cursor to execute SQL commands
        cursor.execute("SELECT * FROM users")  # Retrieve all rows from the "users" table
        users = cursor.fetchall()  # Fetch all records as a list of tuples
    
    # Render the index.html template and pass the retrieved data to it
    return render_template("index.html", users=users)

# Define a route to handle form submissions to add new names
@app.route("/add", methods=["POST"])
def add_user():
    # Retrieve the name input from the form submission
    name = request.form["name"]
    
    # Check if the name is not empty before inserting into the database
    if name:
        with sqlite3.connect("database.db") as conn:
            # Execute an SQL command to insert the new name into the database
            conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()  # Commit the transaction to save changes
    
    # Redirect back to the home page to refresh the displayed names
    return redirect("/")

# Run the application if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode for easier troubleshooting
