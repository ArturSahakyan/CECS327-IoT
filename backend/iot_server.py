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
FRIDGE_2 = "1b8548b7-1e24-4e8a-99d5-93c6ad60c599"
DISHWASHER = "7i1-n8h-5b9-u1s"

# Get Average of a specified field
def avg_of_field(collection, uid, field) -> float:
    query = { "payload.parent_asset_uid": uid }
    documents = collection.find(query)

    # Collect Each Value in a List
    field_values = []
    for doc in documents:
        value = doc["payload"].get(field)
        if value is not None:
            field_values.append(float(value))

    # Average it out if there are values
    if field_values:
        avg = sum(field_values) / len(field_values)
        return avg

    return 0 

# Matches Sensor Nicknames to Real Sensor Names in DB
def get_sensor_name(nickname:str, db) -> str:
    meta_col = db.getCol("IoT_metadata")
    metadata = meta_col.find_one({"customAttributes.additionalMetadata": {"$exists": True}})

    if not metadata:
        print("No metadata document found")
        return ""

    # Pull value from nickname
    custom = metadata.get("customAttributes", {})
    additional = custom.get("additionalMetadata", {})
    sensor = additional.get(nickname)
    if not sensor:
        print("No sensor found")
        return ""

    return sensor

# Respond to Each of the 3 Possible Queries
def query_response(msg: int, db) -> str:
    output = ""

    # Respond Per MSG Codes commented at the top of the code
    match msg:
        case 1:
            output = ""

            # Get Average Percent
            moisture_sensor = get_sensor_name("Moisture", db)
            avg_moist = avg_of_field(db.getCol("IoT_virtual"), FRIDGE_2,
                                     moisture_sensor)

            output = f"Average Relative Humidity was {avg_moist}%"

            return output
        case 2:
            output = ""

            # Average Water Consumption
            avg_water = avg_of_field(db.getCol("IoT_virtual"), DISHWASHER,
                                     "WaterConsumptionSensor")

            output = f"Dishwasher consumes {avg_water} gallons per cycle"

            return output
        case 3:
            output = ""
            # Find Average Current Used
            f1_avg = avg_of_field(db.getCol("IoT_virtual"), FRIDGE_1, "Ammeter")
            dw_avg = avg_of_field(db.getCol("IoT_virtual"), DISHWASHER, "Ammeter-Washer")

            # Find Sensor Name from Metadata for Fridge 2
            f2_sensor = get_sensor_name("Current", db)
            f2_avg = avg_of_field(db.getCol("IoT_virtual"), FRIDGE_2, f2_sensor)

            # Avoid magic numbers
            volt_draw = 120

            # Calc F1 KWH
            f1_kwh = f1_avg * volt_draw # Power in Watts
            f1_kwh /= 1000 # Convert to kWh

            # Calc F2 KWH
            f2_kwh = f2_avg * volt_draw
            f2_kwh /= 1000

            # Calc DW KWH
            dw_kwh = dw_avg * volt_draw
            dw_kwh /= 1000

            # Calculate Largest Consumption
            largest = max(dw_kwh, f1_kwh, f2_kwh)
            if largest == dw_kwh:
                output = "Dishwasher"
            if largest == f1_kwh:
                output = "Fridge 1"
            if largest == f2_kwh:
                output = "Fridge 2"

            output += " has consumed the most electricity"
            output += "\nConsumed: " + str(largest) + " kWh"

            return output

    return output

# Network Connection Values
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
        # Pull PORT from environment or ask if N/A
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
                    client_socket.sendall(query_response(resp, db_delegate).encode())

# Holds Database Object (Wrapper)
class DBDelegate:
    def __init__(self, client):
        self.client = client
        self.db = client["test"] 
    
    def getCol(self, name: str):
        return self.db[name]

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
