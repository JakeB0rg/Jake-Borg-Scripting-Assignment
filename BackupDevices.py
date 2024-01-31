import time
import paramiko
from github import Github
import sqlite3
import socket

# Replace these with your own database and GitHub credentials
db_path = "RouterDatabase.db"
github_token = "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"
repo_name = "Jake-Borg-Scripting-Assignment"

def get_backup_schedule():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT hour, minute FROM backup_schedule')
        schedule = cursor.fetchone()
    return schedule

def get_router_list():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ip, admin_username, admin_password FROM routers')
        routers = cursor.fetchall()
    return routers

def backup_router(router_ip, username, password):
    try:
        # Create SSH client object
        ssh_client = paramiko.SSHClient()

        # Set the policy to automatically add the host keys
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the router using the specified cipher and key exchange algorithms
        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        # Get running configuration
        stdin, stdout, stderr = ssh_client.exec_command("show running-config")
        running_config = stdout.read().decode()

        print(running_config)

        # Save to a local file
        filename = f"{router_ip}.config"
        with open(filename, "w") as file:
            file.write(running_config)
    
    finally:
        # Close the SSH connection
        ssh_client.close()

    return filename
 

def upload_to_github(filename, github_token, repo_name):
    try:
        # Authenticate with GitHub
        g = Github(github_token)

        # Get the repository
        repo = g.get_user().get_repo(repo_name)

        # Upload file to GitHub
        with open(filename, "r") as file:
            content = file.read()
            repo.create_file(filename, f"Backup {filename}", content, branch="main")

        print(f"Backup for {filename} uploaded to GitHub.")
    except Exception as e:
        print(f"Error uploading to GitHub: {str(e)}")

def main():
    while True:
        # Get current time from the database
        schedule = get_backup_schedule()
        db_time = f"{schedule[0]:02d}:{schedule[1]:02d}" if schedule else None

        if db_time:
            # Get the list of routers from the database
            routers = get_router_list()

            # Get current time
            current_time = time.strftime("%H:%M", time.localtime())

            # Print for debugging
            print(f"Current time: {current_time}, Scheduled time: {db_time}")

            # Check if it's time to perform the backup
            if current_time == db_time:
                print("Performing backup...")
                for router in routers:
                    router_ip, admin_username, admin_password = router
                    backup_filename = backup_router(router_ip, admin_username, admin_password)
                    if backup_filename:
                        upload_to_github(backup_filename, github_token, repo_name)
                        print(f"Backup for {router_ip} completed.")

        # Sleep for half a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    main()
    