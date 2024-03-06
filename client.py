import socket
import time


def start_client(host_id, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to peer {host_id}")
    while True:
        msg = 'heartbeat'
        client.send(msg.encode('utf-8'))
        time.sleep(60)


if __name__ == "__main__":
    connections = [
        {"host_id": 1, "host": "localhost", "port": 80}
    ]
    for connection in connections:
        start_client(connection["host_id"], connection["host"], connection["port"])
