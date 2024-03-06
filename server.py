import socket

SERVER_HOST = 'localhost'
SERVER_PORT = 5555
connected_servers = []


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()
    
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
    