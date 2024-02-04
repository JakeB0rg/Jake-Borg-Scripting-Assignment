import socket
import ssl
import sqlite3
import os

DATABASE_PATH = 'RouterDatabase.db'

def init_database(): #this creates the table where the router data will be stored
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT NOT NULL UNIQUE,
            admin_username TEXT NOT NULL,
            admin_password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_router(name, ip): #this function adds a router to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO routers (name, ip, admin_username, admin_password)
            VALUES (?, ?, 'cisco', 'cisco')
        ''', (name, ip))
        conn.commit()
        print(f"Router '{name}' added successfully.")
        return f"Router '{name}' added successfully."
    except sqlite3.IntegrityError:
        print(f"Error: Router with IP '{ip}' already exists in the database.")
        return f"Router with IP '{ip}' already exists in the database"
    finally:
        conn.close()
        

def delete_router(ip): #and this one removes a router from the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routers WHERE ip = ?", (ip,))
    if cursor.rowcount > 0:
        print(f"Router with IP '{ip}' deleted successfully.")    
        conn.commit()
        conn.close()
        return f"Router with IP '{ip}' deleted successfully"
    else:
        print(f"Error: No router found with IP '{ip}'.")
        conn.commit()
        conn.close()
        return f"No router found with IP '{ip}'."


def list_routers(): #this lists the routers
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, ip, admin_username, admin_password FROM routers")
    routers = cursor.fetchall()
    for router in routers:
        print(f"ID: {router[0]}, Name: {router[1]}, IP: {router[2]}, Username: {router[3]}, Password: {router[4]}")
    routers_info = []
    conn.close()
    for router in routers:
        routers_info.append(f"ID: {router[0]}, Name: {router[1]}, IP: {router[2]}, Username: {router[3]}, Password: {router[4]}")
    return "\n".join(routers_info)


def start_server(): #this starts the server side of the socket
    init_database()

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
    
    ssl_context.load_cert_chain(certfile='homeserver-cert.pem', keyfile='homeserver-key.pem') #uses the cert and key

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)

    print("Server listening on port 12345...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            ssl_socket = ssl_context.wrap_socket(client_socket, server_side=True)

            request = ssl_socket.recv(1024).decode('utf-8')
            if request.startswith("ADD"): #this is what runs the add function.
                _, name, ip = request.split()
                response = add_router(name, ip)
            elif request.startswith("DELETE"):  #this runs the delete
                _, ip = request.split()
                response = delete_router(ip)
            elif request.startswith("LIST"):    #this runs the list function.
                response = list_routers()
            else:
                response = "Invalid request."

            ssl_socket.send(response.encode('utf-8')) #responses are sent back to the client, ie main program.

            ssl_socket.close()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()