import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('RouterDatabase.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS routers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ip TEXT NOT NULL UNIQUE,
        admin_username TEXT NOT NULL,
        admin_password TEXT NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
