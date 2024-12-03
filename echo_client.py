import socket
import ipaddress

RECV_BYTES = 1024

def start_client():
    while True:
        ip = input("Enter IP: ")
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print("Invalid IP")
            continue

        try:
            port = int(input("Enter Port: "))
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            print("Port Number Wrong")
            continue

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((ip, port))
            except (socket.error, ConnectionRefusedError) as e:
                print(f"Error {e}")
                continue

            while True:
                msg = input("Enter MSG: ")
                if msg.lower() == "q!" or msg == "":
                    return

                client_socket.sendall(msg.encode())
                resp = client_socket.recv(RECV_BYTES)
                print(f"Server Responded: {resp.decode()}")

if __name__ == "__main__":
    start_client()