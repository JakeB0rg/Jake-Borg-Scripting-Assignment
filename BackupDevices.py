import time
from datetime import datetime
import sqlite3
import paramiko
from github import Github

# SQLite database path
DATABASE_PATH = 'RouterDatabase.db'

# GitHub repository details
GITHUB_TOKEN = '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'
GITHUB_REPO_OWNER = 'JakeB0rg'
GITHUB_REPO_NAME = 'your_github_repo_name'

def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backup_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_backup_schedule(hour, minute):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO backup_schedule (hour, minute) VALUES (?, ?)', (hour, minute))
    conn.commit()
    conn.close()

def get_backup_schedule():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT hour, minute FROM backup_schedule')
    schedule = cursor.fetchone()
    conn.close()
    return schedule

def perform_backup(router_ip):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the router using SSH
        ssh_client.connect(router_ip, username='your_username', password='your_password')

        # Get the running configuration
        stdin, stdout, stderr = ssh_client.exec_command('show running-config')
        running_config = stdout.read().decode('utf-8')

        # Save the running configuration to a local file
        filename = f'{router_ip}.config'
        with open(filename, 'w') as f:
            f.write(running_config)

        return filename
    finally:
        ssh_client.close()

def upload_to_github(filename):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user(GITHUB_REPO_OWNER).get_repo(GITHUB_REPO_NAME)
    contents = repo.get_contents(filename, ref='main')
    
    with open(filename, 'rb') as data:
        repo.update_file(contents.path, f'Daily Backup - {datetime.now().strftime("%Y-%m-%d")}', data.read(), contents.sha)

def main():
    init_database()

    while True:
        current_time = time.localtime()
        backup_schedule = get_backup_schedule()

        if backup_schedule and current_time.tm_hour == backup_schedule[0] and current_time.tm_min == backup_schedule[1]:
            # Get the list of routers from the database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT ip FROM routers')
            routers = cursor.fetchall()
            conn.close()

            # Perform backup for each router
            for router in routers:
                router_ip = router[0]
                filename = perform_backup(router_ip)
                upload_to_github(filename)

            print(f'Backups completed at {time.strftime("%H:%M:%S")}.')

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
