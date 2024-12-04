import socket
import ipaddress
import os

from typing import Tuple
from pymongo import MongoClient

"""
    MSG Codes:
        1 - Avg moisture inside kitchen fridge
        2 - Avg water consumption per cycle in dishwasher
        3 - Which device consumed more electricity
"""

# Asset IDs
FRIDGE_1 = "8ks-s9n-zpx-176"
FRIDGE_2 = "1b8548b7-1e24-4e8a-99d5-93c6ad60c5991b8548b7-1e24-4e8a-99d5-93c6ad60c599"
DISHWASHER = "7i1-n8h-5b9-u1s"

def query_response(msg: int) -> str:
    output = ""

    # Respond Per MSG Codes commented at the top of the code
    match msg:
        case 1:
            output = "Kitchen Fridge has a lot of moisture"
            return output
        case 2:
            output = "A lot of water consumed per cycle"
            return output
        case 3:
            output = "fridge 2 consumed most energy"
            return output

    return output

MAX_CONNECTIONS = 5
RECV_BYTES = 1024

# Collection & Validate IP and Port information
def validate_server() -> Tuple[str, int]:
    # Default to 0.0.0.0 for now
    host_ip = "0.0.0.0" 
    try:
        ipaddress.ip_address(host_ip)
    except ValueError:
        print("Invalid IP Address..")
        exit()

    try:
        host_port = int(os.getenv("PORT", -1))
        if host_port == -1:
            host_port = int(input("Enter host port: "))
        if host_port < 1 or host_port > 65535:
            raise ValueError()
    except ValueError:
            print("Invalid Port")
            exit()

    return (host_ip, host_port)

# Create TCP Connection to recieve data
def start_server(host, port, db_delegate):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(MAX_CONNECTIONS)

        while True:
            client_socket, address = server_socket.accept()
            with client_socket:
                while True:
                    msg = client_socket.recv(RECV_BYTES)
                    if not msg:
                        break

                    # MSG is guaranteed to be valid int already
                    resp = int(msg.decode())
                    client_socket.sendall(query_response(resp).encode())

class DBDelegate:
    def __init__(self, client):
        self.client = client
        self.db = client["test"] 

if __name__ == "__main__":
    # Initialize MongoDB
    db_user = os.getenv("DBUSER", "error")
    db_pass = os.getenv("DBPASS", "error")

    client = MongoClient("mongodb+srv://"+db_user+":"+db_pass+
                         "@cecs327-cluster.sjfta.mongodb.net/"+
                         "?retryWrites=true&w=majority&appName=cecs327-cluster")
    db_delegate = DBDelegate(client)
    

    # SetUp TCP Server
    net_id = validate_server()
    start_server(net_id[0], net_id[1], db_delegate)
