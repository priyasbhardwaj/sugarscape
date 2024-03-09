import socket
import time

HEARTBEAT_REQUEST = "GET_ACTIVE_SERVERS"


def start_client(host_id, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to peer {host_id}")
    active_count = 0
    while True:
        # Get active server count via heartbeat check (repeats check every 1 minute)
        client.send(HEARTBEAT_REQUEST.encode("utf-8"))
        active_count_bytes = client.recv(1024)
        active_count = int.from_bytes(active_count_bytes, byteorder="big")
        print(f"There are: {active_count} active servers in the network. ")
        time.sleep(60)


if __name__ == "__main__":
    connections = [{"host_id": 1, "host": "localhost", "port": 8001}]
    for connection in connections:
        start_client(connection["host_id"], connection["host"], connection["port"])
