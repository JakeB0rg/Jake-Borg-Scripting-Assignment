import sqlite3

def init_database():
    conn = sqlite3.connect('RouterDatabase.db') #connects to the database, creates it if it doesnt exist

    cursor = conn.cursor()

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS routers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT NOT NULL UNIQUE,
            admin_username TEXT NOT NULL,
            admin_password TEXT NOT NULL
        )
    ''') #data is SQL injected direcetly 

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
