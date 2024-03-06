import socket
import threading

PORT = 80


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen()
    print(f"Server listening on port: {PORT}")

    while True:
        client, address = server.accept()
        client_listener = threading.Thread(target=listener, args=(client, address))
        client_listener.start()


def listener(client, address):
    print(f"Connection established with {address}")

    while True:
        msg = client.recv(1024)
        if not msg:
            break
        print(f"Received message from {address}: {msg.decode('utf-8')}")
    print(f"Connection closed")


if __name__ == "__main__":
    start_server()

    