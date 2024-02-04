import socket                                         #This communicates with ManageDevices
import ssl                                            #This creates the TLS security
import sqlite3                                        #This is for database operations
import time                                           #This is needed for time-related operations
from datetime import datetime                         #This is for Date/time related stuff
import paramiko                                       #This is needed for SSH related stuff
import requests                                       #This is for retreiving github stuff
import matplotlib.pyplot as plt                       #This plots the piechart
from elasticsearch import Elasticsearch, helpers      #This communicates with the elasticsearch

DATABASE_PATH = 'RouterDatabase.db'

def init_database():    #This initiates the table in the database that stores the backup time
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

def input_database(hour, minute): #This inputs the backup time into the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            REPLACE INTO backup_schedule (id, hour, minute)
            VALUES (1, ?, ?)
        ''', (hour, minute))
        conn.commit()
        print(f"Time inputted successfully")
    except sqlite3.IntegrityError:
        print(f"Error")
    finally:
        conn.close()

def send_request(request): #This sends the request to the ManageDevices program, used in options a-c
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = ssl.wrap_socket(client_socket, keyfile=None, certfile=None, server_side=False, ssl_version=ssl.PROTOCOL_TLSv1_2) #i could not get this to work with TLS1.3
    ssl_socket.send(request.encode('utf-8'))

    response = ssl_socket.recv(1024).decode('utf-8') #receives the output from managedevices and prints it
    print(response)
    
    ssl_socket.close()
    
def ssh_Enable_Netflow(): #This sends the required commands to a given router to enable netflow
    
    router_ip = input("Enter the IP address of the router: ")
    username = 'cisco'
    password = 'cisco'

    commands = [ #These are the commands sent to the router via SSH
        'conf t',
        'ip flow-cache timeout inactive 10',
        'ip flow-cache timeout active 1',
        'ip flow-export source FastEthernet0/0',
        'ip flow-export version 9',
        'ip flow-export destination 192.168.122.1 2055',
        'interface FastEthernet0/0',
        'ip flow ingress',
        'ip flow egress',
        'exit',
        'exit',
        'write memory'
    ]

    try:
        ssh_client = paramiko.SSHClient() #initiates ssh through paramiko

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #creates policy to automatically adds host keys

        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False) #connects to router 

        ssh_shell = ssh_client.invoke_shell() #this creates an interactive shell for inputting the commands
        time.sleep(1)

        print("Applying commands... this may take a few seconds.")
        for command in commands: #the commands are inputted one by one, with a delay in between
            ssh_shell.send(command + '\n')
            time.sleep(1)

        print("This router has been configured for NetFlowV9")

        ssh_client.close()

    except paramiko.AuthenticationException: #exceptions in case the code breaks
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as ssh_err:
        print(f"Unable to establish SSH connection: {ssh_err}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def ssh_Disable_Netflow():#This is a copy of ssh_Enable_Netflow but with disable commands
    router_ip = input("Enter the IP address of the router: ")
    username = 'cisco'
    password = 'cisco'

    commands = [ 
        'conf t',
        'no ip flow-cache timeout inactive 10',
        'no ip flow-cache timeout active 1',
        'no ip flow-export source FastEthernet0/0',
        'no ip flow-export version 9',
        'no ip flow-export destination 192.168.122.1 2055',
        'interface FastEthernet0/0',
        'no ip flow ingress',
        'no ip flow egress',
        'exit',
        'exit',
        'write memory'
    ]

    try:
        ssh_client = paramiko.SSHClient() #initiates ssh through paramiko

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #creates policy to automatically adds host keys

        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False) #connects to router 

        ssh_shell = ssh_client.invoke_shell() #this creates an interactive shell for inputting the commands
        time.sleep(1)

        print("Applying commands... this may take a few seconds.")
        for command in commands: #the commands are inputted one by one, with a delay in between
            ssh_shell.send(command + '\n')
            time.sleep(1)

        print("This router no longer has NetflowV9")

        ssh_client.close()

    except paramiko.AuthenticationException: #exceptions in case the code breaks
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as ssh_err:
        print(f"Unable to establish SSH connection: {ssh_err}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def ssh_Enable_SNMP():#This is a copy of ssh_Enable_Netflow but with SNMP commands
    router_ip = input("Enter the IP address of the router: ")
    username = 'cisco'
    password = 'cisco'

    commands = [ 
        'conf t',
        'logging history debugging',
        'snmp-server community SFN RO',
        'snmp-server ifindex persist',
        'snmp-server enable traps snmp linkdown linkup',
        'snmp-server enable traps syslog',
        'snmp-server host 192.168.122.1 version 2c SFN',
        'exit',
        'exit',
        'write memory'
    ]

    try:
        ssh_client = paramiko.SSHClient()

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        ssh_shell = ssh_client.invoke_shell()
        time.sleep(1)

        print("Applying commands... this may take a few seconds.")
        for command in commands:
            ssh_shell.send(command + '\n')
            time.sleep(1)  # delay

        print("This router has been configured for SNMP")

        ssh_client.close()

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as ssh_err:
        print(f"Unable to establish SSH connection: {ssh_err}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def ssh_Disable_SNMP():#This is a copy of ssh_Enable_Netflow but with disable SNMP commands
    router_ip = input("Enter the IP address of the router: ")
    username = 'cisco'
    password = 'cisco'

    commands = [ 
        'conf t',
        'no logging history debugging',
        'no snmp-server community SFN RO',
        'no snmp-server ifindex persist',
        'no snmp-server enable traps snmp linkdown linkup',
        'no snmp-server enable traps syslog',
        'no snmp-server host 192.168.122.1 version 2c SFN',
        'exit',
        'exit',
        'write memory'
    ]

    try:
        ssh_client = paramiko.SSHClient()

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(router_ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        ssh_shell = ssh_client.invoke_shell()
        time.sleep(1)

        print("Applying commands... this may take a few seconds.")
        for command in commands:
            ssh_shell.send(command + '\n')
            time.sleep(1)  # delay
            output = ssh_shell.recv(65535).decode()
            print(output)

        print("This router has been configured for SNMP")

        ssh_client.close()

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as ssh_err:
        print(f"Unable to establish SSH connection: {ssh_err}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def fetch_config(ip_address): #This fetches the latest config from github 
    base_url = "https://raw.githubusercontent.com/JakeB0rg/Jake-Borg-Scripting-Assignment/main/"

    config_url = base_url + ip_address + ".config" #building the URL to get the code

    try:
        response = requests.get(config_url) #Sends a GET request to fetch the config file
        if response.status_code == 200:
            print("Config file for IP address", ip_address + ":") #Prints the contents of the config file
            print(response.text)
        else:
            print("Config file for IP address", ip_address, "not found.")
    except Exception as e:
        print("An error occurred:", str(e))

def fetch_previous(ip_address, date): #This fetches the version specified and then runs the fetch_config function to compare
   
    base_url = "https://api.github.com/repos/JakeB0rg/Jake-Borg-Scripting-Assignment/commits"

    commits_url = f"{base_url}?path={ip_address}.config&since={date}T00:00:00Z" #constructing the URL to fetch the specified file

    try:
        
        response = requests.get(commits_url) #Sends the GET request to fetch commits

        if response.status_code == 200:
            commits = response.json()

            if len(commits) > 0:

                #This finds the first commit after the specified date, using the sha of the commited file
                commit_sha = commits[0]['sha']
                content_url = f"https://raw.githubusercontent.com/JakeB0rg/Jake-Borg-Scripting-Assignment/{commit_sha}/{ip_address}.config"
                content_response = requests.get(content_url)

                if content_response.status_code == 200:
                    print(f"Config file for IP address {ip_address} on {date}:") #prints the header
                    print(content_response.text)    #prints whatever is in the config file
                else:
                    print(f"Config file for IP address {ip_address} on {date} not found.")
            else:
                print(f"No commits found for IP address {ip_address} after {date}.")

        else:
            print(f"Error fetching commits for IP address {ip_address}.")
        
        print("#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n") #this just creates a lot of hash character so you can see where the 2 configs are separated
        print(f"Config file for IP address {ip_address} on {date}:") 
        fetch_config(ip_address) #this runs the fetch config so the user sees the latest config file.

    except Exception as e:
        print("An error occurred:", str(e)) #error handling :)

def Statistics(ip): #This displays the pie chart which shows the number of grouped packets per ip address

    conn = sqlite3.connect('RouterDatabase.db') #connecting to db
    cursor = conn.cursor()

    cursor.execute("SELECT num_packets, protocol FROM netflow WHERE router_ip = ? GROUP BY num_packets", (ip,))
    protocol_packets = cursor.fetchall() #get required data from the db
    conn.close()

    protocols = [row[0] for row in protocol_packets] #extracts the data 
    packets = [row[1] for row in protocol_packets]

    plt.figure(figsize=(8, 8))  #this creates the pie chart
    plt.pie(packets, labels=protocols, autopct='%1.1f%%', startangle=140)
    plt.title('Packet Percentage per Protocol for Router {}'.format(ip))
    plt.axis('equal')  #Equal aspect ratio ensures that pie is drawn as a circle.
    
    plt.show() #Show the pie chart

def datecheck_before_back(ip_address, date_str): #this makes sure the date enterred is valid
    try:
        date = datetime.strptime(date_str, "%d-%m-%Y").isoformat()
    except ValueError:
        print("Invalid date format. Please use DD-MM-YYYY.")
    else:
        fetch_previous(ip_address, date)

def show_router_syslog(router_ip):  #broken: meant to show the elasticsearch results
    try:
        con = sqlite3.connect("RouterDatabase.db")         #Connects to db
        cur = con.cursor()
        query = "SELECT * FROM SYSLOG WHERE ROUTER_IP = ?"
        cur.execute(query, (router_ip,))
        data = cur.fetchall()
        
        CLOUD_ID = "SFN:ZXVyb3BlLXdlc3QyLmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkNzBkZGM3N2Q5ZDIzNDJlOThjYzQ1Y2NkY2IzZWU1OWQkMjAxNTU3NjMyMjUzNDFkMTg3ZTQ3ZDljMTUxNDNlNTU="
        API_KEY = "aWowVWRJMEJvVV82ek92NzZQU2I6MzF3SlVXMUpUakMya0REa2RBRXdJUQ=="
        es = Elasticsearch( #these are needed to access the elasticsearch API
            cloud_id=CLOUD_ID,
            api_key=API_KEY,
        )

        index_settings = { #Index settings and mappings
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "ID": {"type": "integer"},
                    "date": {"type": "date"},
                    "time": {"type": "keyword"},
                    "router_ip": {"type": "ip"},
                    "message": {"type": "text"}
                }
            }
        }

        index_name = "syslog" #these lines create the index if it doesnt exist
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_settings)
            print(f"Index '{index_name}' created successfully.")
        else:
            print(f"Index '{index_name}' already exists.")

        actions = [ #this just formats the instructions for the api
            {
                "_op_type": "index",
                "_index": 'syslog',
                "_source": {
                    "ID": row[0],
                    "date": row[1],
                    "time": row[2],
                    "router_ip": row[3],
                    "message": row[4]
                }
            }
            for row in data
        ]

        helpers.bulk(es, actions) #Bulks insert into Elasticsearch

        search_querydown = {         # Defines search queries after data insertion
            "query": {
                "bool": {
                    "must": [
                        {"term": {"router_ip": router_ip}},
                        {"match": {"message": "DOWN"}}
                    ]
                }
            }
        }
        search_queryup = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"router_ip": router_ip}},
                        {"match": {"message": "UP"}}
                    ]
                }
            }
        }

        #Perform searches
        print("Executing search_querydown:", search_querydown)
        search_result = es.search(index='syslog', body=search_querydown)
        print("Search result for DOWN messages:", search_result)

        print("Executing search_queryup:", search_queryup)
        search_result2 = es.search(index='syslog', body=search_queryup)
        print("Search result for UP messages:", search_result2)

        #Prints the search results
        for hit in search_result.get('hits', {}).get('hits', []):
            print(f"DOWN Message - Timestamp: {hit['_source']['time']}, Message: {hit['_source']['message']}")

        for hit in search_result2.get('hits', {}).get('hits', []):
            print(f"UP Message - Timestamp: {hit['_source']['time']}, Message: {hit['_source']['message']}")


    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally: #this closes everything related
        if con:
            con.close()
        if es:
            es.transport.close()


if __name__ == "__main__": #this is where the code begins
    init_database() #initiates database prior to user selection
    while True:
        print("\nOptions:")
        print("a. Add Router")
        print("b. Delete Router")
        print("c. List Routers")
        print("d. Set Backup Time")
        print("e. Set Router Netflow Settings")
        print("f. Remove Router Netflow Settings")
        print("g. Set Router SNMP Settings")
        print("h. Remove Router SNMP Settings")
        print("i. Show Router Config")
        print("j. Show Changes in Router Config")
        print("k. Display Router Netflow Statistics")
        print("l. Show Router Syslog")
        print("z. Exit")

        choice = input("Enter your choice: ")

        if choice == 'a': #the option to add/list/delete is placed in the send request. 
            name = input("Enter router name: ")
            ip = input("Enter router IP: ")
            send_request(f"ADD {name} {ip}")

        elif choice == 'b':
            ip = input("Enter router IP to delete: ")
            send_request(f"DELETE {ip}")

        elif choice == 'c':
            send_request("LIST")

        elif choice == 'd':
            hour = int(input("Enter backup hour (0-23): ")) #user inputs hour and minute seperately
            minute = int(input("Enter backup minute (0-59): "))
            input_database(hour, minute)

        elif choice == 'e': #these are self-explanitory
             ssh_Enable_Netflow()

        elif choice == 'f':
            ssh_Disable_Netflow()

        elif choice == 'g':
            ssh_Enable_SNMP()
        
        elif choice == 'h':
            ssh_Disable_SNMP()

        elif choice == 'i':
            ip_address = input("Enter the IP address: ")
            fetch_config(ip_address)
        
        elif choice == 'j':
                ip_address = input("Enter IP address: ")
                date_str = input("Enter date (DD-MM-YYYY): ")
                datecheck_before_back(ip_address, date_str)
        
        elif choice == 'k':
            ip = input('Enter the Router IP you wish to see statistics for: ')
            Statistics(ip)
        
        elif choice == 'l':
            router_ip = input("Input Router IP: ")
            show_router_syslog(router_ip)

        elif choice == 'z': #this closes the program
            print("Shutting Down...")
            break
        else:
            print("Invalid choice. Please enter a valid choice")
