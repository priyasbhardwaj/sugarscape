import json
import os
import socket
import subprocess
import time

HEARTBEAT_REQUEST = "GET_ACTIVE_SERVERS"


def run_make_seeds():
    subprocess.run(["make", "seeds"], check=True)
    os.chdir('..')  # Return to the original directory


def get_config_files():
    config_path = os.path.join(os.getcwd(), 'data')
    return [os.path.join(config_path, f) for f in os.listdir(config_path) if f.endswith('.config')]


def send_message(client_socket, message):
    serialized_message = json.dumps(message) + "\n"  # Add newline as delimiter
    client_socket.send(serialized_message.encode('utf-8'))


def send_config_files(client_socket):
    try:
        # Generate .config files
        run_make_seeds()

        # Send .config files to server
        for config_file in get_config_files():
            with open(config_file, 'r') as file:
                config_content = file.read()
                send_message(client_socket,
                             {"type": "config_file", "data": config_content, "filename": os.path.basename(config_file)})

        # Notify server of transfer completion
        send_message(client_socket, {"type": "transfer_complete"})
        print("All .config files sent to server.")

    finally:
        client_socket.close()


def start_client(host_id, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to peer {host_id}")
    send_config_files(client)
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
