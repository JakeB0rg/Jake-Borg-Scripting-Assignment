import socket
import ssl
import sqlite3

DATABASE_PATH = 'RouterDatabase.db'

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

def input_database(hour, minute):
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

def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = ssl.wrap_socket(client_socket, keyfile=None, certfile=None, server_side=False, ssl_version=ssl.PROTOCOL_TLSv1_2)
    ssl_socket.connect(('localhost', 12345))
    ssl_socket.send(request.encode('utf-8'))

        # Receive and print the server's response
    response = ssl_socket.recv(1024).decode('utf-8')
    print(response)
    
    ssl_socket.close()

                                            

if __name__ == "__main__":
    init_database()
    while True:
        print("\nOptions:")
        print("1. Add Router")
        print("2. Delete Router")
        print("3. List Routers")
        print("4. Set Backup Time")
        print("5. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            name = input("Enter router name: ")
            ip = input("Enter router IP: ")
            send_request(f"ADD {name} {ip}")
        elif choice == '2':
            ip = input("Enter router IP to delete: ")
            send_request(f"DELETE {ip}")
        elif choice == '3':
            send_request("LIST")
        elif choice == '4':
             # Option to set backup time
            hour = int(input("Enter backup hour (0-23): "))
            minute = int(input("Enter backup minute (0-59): "))
            input_database(hour, minute)
            
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
