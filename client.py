import socket

LOCAL_SERVER = 'localhost'
SERVER_PORT = 5555

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((LOCAL_SERVER, SERVER_PORT))
    client.listen()
        