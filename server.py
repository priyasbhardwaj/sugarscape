import json
import os
import shutil
import socket
import subprocess
import threading
import sys
from contextlib import closing

# PORT = 80
HEARTBEAT_REQUEST = "GET_ACTIVE_SERVERS"

# all known server addresses in network
# TO BE CHANGED: Replace with actual addresses and ports
SERVERS = {
    "server1": ("localhost", 5520),
    "server2": ("localhost", 5521),
    "server3": ("localhost", 5522),
    "server4": ("localhost", 5523),
}

TEMP_DIR = 'temp'
DATA_DIR = 'data'


def setup_directories():
    os.makedirs(TEMP_DIR, exist_ok=True)


def move_files_from_temp_to_data():
    for filename in os.listdir(TEMP_DIR):
        shutil.move(os.path.join(TEMP_DIR, filename), DATA_DIR)
    shutil.rmtree(TEMP_DIR)  # Optionally remove TEMP_DIR after moving files


def recv_files_from_client(client_socket, address):
    buffer = ""
    while True:
        chunk = client_socket.recv(4096).decode('utf-8')
        if not chunk:
            break
        buffer += chunk

        while '\n' in buffer:
            message_end = buffer.index('\n') + 1
            message = json.loads(buffer[:message_end])
            buffer = buffer[message_end:]

            if message['type'] == 'config_file':
                filepath = os.path.join(TEMP_DIR, message['filename'])
                with open(filepath, 'w') as file:
                    file.write(message['data'])
                print(f"Received and saved {message['filename']}")
            elif message['type'] == 'transfer_complete':
                print("Received transfer_complete message")
                move_files_from_temp_to_data()
                print("All .config files moved to data directory.")
                break  # Exit after handling transfer_complete


# return count of active servers and list of active server names
def check_active_servers(my_server_address, my_name):
    active_count = 1  # Including itself in the count

    active_servers = [my_name]  # Names of active servers, initialize with self
    for server_name in SERVERS:
        server_addr = SERVERS[server_name]
        if server_addr == my_server_address:
            continue  # Skip itself to avoid duplicate count
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(server_addr) == 0:
                active_count += 1
                active_servers.append(server_name)
    return active_count, active_servers


# heartbeat check to get number of servers (including self) in the network and their names
# returns active_count to main server function
def heartbeat_check():
    active_count, active_servers = check_active_servers(my_server_address, my_name)
    print(f"There are: {active_count} active servers in the network. ")
    print("List of active servers (including current server): ")
    for n in active_servers:
        print(n)
    return active_count


def run_simulation():
    subprocess.run(["make", "data"], check=True)


def start_server(my_server_address, my_name):
    setup_directories()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(my_server_address)
    server.listen()
    print(f"Server listening on port: {my_port}")
    active_count = heartbeat_check()

    while True:
        client, address = server.accept()
        client_listener = threading.Thread(
            target=listener, args=(client, address, active_count)
        )
        client_listener.start()


def listener(client, address, active_count):
    print(f"Connection established with {address}")
    while True:
        msg = client.recv(1024)
        if not msg:
            break
        decoded_msg = msg.decode("utf-8")
        print(f"Received message from {address}: {decoded_msg}")
        # check for heartbeat request from client
        if decoded_msg == HEARTBEAT_REQUEST:
            active_count = heartbeat_check()
            active_count_bytes = active_count.to_bytes(4, byteorder="big")
            client.send(active_count_bytes)
    recv_files_from_client(client, address)
    run_simulation()
    print(f"Connection closed")


if __name__ == "__main__":
    # for now takes in port number from command arg to test
    if len(sys.argv) != 2:
        print("Usage: server.py <port_number>")
        sys.exit(1)
    my_port = int(sys.argv[1])
    # This server's address and port
    my_server_address = ("localhost", my_port)
    my_name = ""
    for name in SERVERS:
        if SERVERS[name] == my_server_address:
            my_name = name
    start_server(my_server_address, my_name)
