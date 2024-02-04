import time
import paramiko
from github import Github
import sqlite3
import socket

#these are required to communicate with github
db_path = "RouterDatabase.db"
github_token = "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"
repo_name = "Jake-Borg-Scripting-Assignment"

def get_backup_schedule(): #this gets the schedule from the database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT hour, minute FROM backup_schedule')
        schedule = cursor.fetchone()
    return schedule

def get_router_list(): #this gets all the routers in the database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ip, admin_username, admin_password FROM routers')
        routers = cursor.fetchall()
    return routers

def backup_router(router_ip, username, password): #this accesses the router via ssh and takes the config to save in a file
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        stdin, stdout, stderr = ssh_client.exec_command("show running-config") #this sends the command into the router via ssh
        running_config = stdout.read().decode()

        print(running_config)
        
        filename = f"{router_ip}.config" #Saves to a local file
        with open(filename, "w") as file:
            file.write(running_config)
    
    finally:
        # Close the SSH connection
        ssh_client.close()

    return filename
 

def upload_to_github(filename, github_token, repo_name): #this takes the saved file and uploads it to github
    try:
        g = Github(github_token) #this is required for gitbhub auth

        repo = g.get_user().get_repo(repo_name)

        contents = repo.get_contents(filename) #checks if file exists
        sha = contents.sha if contents else None

        with open(filename, "r") as file:
            content = file.read()

        if sha: #if the file exists, it is updated
            repo.update_file(filename, f"Update {filename}", content, sha)

        else: #otherwise, the file is created
            repo.create_file(filename, f"Create {filename}", content, branch="main")


        print(f"Backup for {filename} uploaded to GitHub.")

    except Exception as e:
        print(f"Error uploading to GitHub: {str(e)}")

def main(): #this is the main function
    while True:
        schedule = get_backup_schedule()
        db_time = f"{schedule[0]:02d}:{schedule[1]:02d}" if schedule else None #this gets the time in the database

        if db_time: 
            routers = get_router_list() 

            current_time = time.strftime("%H:%M", time.localtime()) #gets current time

            print(f"Current time: {current_time}, Scheduled time: {db_time}") #this can be removed if desired

            if current_time == db_time: #when the current time is the same as the backup time, this section runs
                print("Performing backup...")
                for router in routers: #runs for every given router
                    router_ip, admin_username, admin_password = router
                    backup_filename = backup_router(router_ip, admin_username, admin_password)
                    if backup_filename:
                        upload_to_github(backup_filename, github_token, repo_name)
                        print(f"Backup for {router_ip} completed.")

        
        time.sleep(60) # Sleep for a minute before checking again

if __name__ == "__main__":
    main()
    