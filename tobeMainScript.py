import socket
import ssl


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
    while True:
        print("\nOptions:")
        print("1. Add Router")
        print("2. Delete Router")
        print("3. List Routers")
        print("4. Exit")

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
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
