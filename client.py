import json
import math
import os
import socket
import subprocess
import time
import struct
import threading

HEARTBEAT_REQUEST = "GET_ACTIVE_SERVERS"
SERVERS = {
    "server1": ("localhost", 5520),
    "server2": ("localhost", 5521),
    "server3": ("localhost", 5522),
    "server4": ("localhost", 5523),
}


def run_make_seeds():
    subprocess.run(["make", "seeds"], check=True)
    os.chdir("..")  # Return to the original directory


def get_config_files():
    path = os.path.join(os.getcwd(), "sugarscape")
    config_path = os.path.join(path, "data")
    return [
        os.path.join(config_path, f)
        for f in os.listdir(config_path)
        if f.endswith(".config")
    ]


def send_message(client_socket, message):
    serialized_message = json.dumps(message) + "\n"  # Add newline as delimiter
    client_socket.send(serialized_message.encode("utf-8"))


def send_config_files(client_socket):
    # Generate .config files
    run_make_seeds()

    # Send .config files to server
    for config_file in get_config_files():
        with open(config_file, "r") as file:
            config_content = file.read()
            send_message(
                client_socket,
                {
                    "type": "config_file",
                    "data": config_content,
                    "filename": os.path.basename(config_file),
                },
            )

    # Notify server of transfer completion
    send_message(client_socket, {"type": "transfer_complete"})
    print("All .config files sent to server.")


def divide_config_files(active_count):
    run_make_seeds()
    data_list = get_config_files()
    num_configs = len(data_list)
    config_per_server = math.ceil(num_configs / active_count)
    divided_config = [
        data_list[i : i + config_per_server]
        for i in range(0, num_configs, config_per_server)
    ]
    return divided_config


def send_config_to_server(host, port, configs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        for config in configs:
            with open(config, "r") as file:
                config_content = file.read()
                send_message(
                    client_socket,
                    {
                        "type": "config_file",
                        "data": config_content,
                        "filename": os.path.basename(config),
                    },
                )

        # Notify server of transfer completion
        send_message(client_socket, {"type": "transfer_complete"})
    print("All .config files sent to server.")


def send_divided_configs(active_count):
    divided_config = divide_config_files(active_count)
    for server_name, (host, port) in SERVERS.items():
        configs = divided_config.pop(0)
        send_config_to_server(host, port, configs)


def collect_sim_time(host_id, host, port, sim_times):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        print(f"Connected to server {host_id} at {host}:{port}")

        sim_data = client.recv(4)
        sim_time = struct.unpack("f", sim_data)[0]
        sim_times.append(sim_time)
        print(f"Received simulation time from {host_id}: {sim_time} seconds")


def start_client(host_id, host, port):
    # Connect to initial server and get number of active servers in network
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to peer {host_id}")
    active_count = 0
    client.send(HEARTBEAT_REQUEST.encode("utf-8"))
    active_count_bytes = client.recv(1024)
    active_count = int.from_bytes(active_count_bytes, byteorder="big")
    client.close()
    send_divided_configs(active_count)

    # Collect simulation times in parallel
    sim_times = []
    threads = []

    for host_id, (host, port) in SERVERS.items():
        thread = threading.Thread(
            target=collect_sim_time, args=(host_id, host, port, sim_times)
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # get max simulation time from the 4 threads, this is the speed of the p2p network
    if sim_times:
        max_time = max(sim_times)
        print(
            f"The maximum simulation time received from the servers is: {max_time} seconds"
        )

    while True:
        # Get active server count via heartbeat check (repeats check every 1 minute)
        client.send(HEARTBEAT_REQUEST.encode("utf-8"))
        active_count_bytes = client.recv(1024)
        active_count = int.from_bytes(active_count_bytes, byteorder="big")
        print(f"There are: {active_count} active servers in the network. ")
        time.sleep(60)


if __name__ == "__main__":
    connections = [{"host_id": 1, "host": "localhost", "port": 5520}]
    for connection in connections:
        start_client(connection["host_id"], connection["host"], connection["port"])
