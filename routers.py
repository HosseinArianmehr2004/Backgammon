import socket
import pickle
import pyshark
import asyncio
import threading
from cryptography.fernet import Fernet


class Router:
    def __init__(self, id, address, neighbors_addresses):
        self.id = id
        self.address = address
        self.conn = None

        self.all_keys = None
        self.key = None

        self.neighbors = neighbors_addresses
        self.neighbors_conns = {}
        for ngh_addr in neighbors_addresses:
            self.neighbors_conns[ngh_addr] = None

        self.clients = {}
        self.routers_ports = []

    def send_to_server(self, conn, addr):
        while True:
            msg = conn.recv(1024)
            cipher = Fernet(self.key)

            if self.id == "R1":
                msg = cipher.decrypt(msg).decode("utf-8")
                msg = f"{msg}@{addr}".encode("utf-8")
            else:
                msg, addr = msg.decode("utf-8").split("@")
                msg = msg.encode("utf-8")
                msg = cipher.decrypt(msg).decode("utf-8")
                msg = f"{msg}@{addr}".encode("utf-8")

            print(f"msg to send: {msg}")
            self.send_to_neighbors(msg)

    # actualy receive from server
    def receive_from_a_neighbor(self, ngh_conn, ngh_addr):
        while True:
            msg = ngh_conn.recv(1024)
            if self.key == None:
                keys = pickle.loads(msg)
                self.all_keys = keys

                if self.id == "R1":
                    self.key = keys[2]
                elif self.id == "R2":
                    self.key = keys[1]
                elif self.id == "R3":
                    self.key = keys[0]
                elif self.id == "R4":
                    self.key = keys[3]

                print(self.key)

            else:
                msg = msg.decode("utf-8")
                print(f"msg received from {ngh_addr}: {msg}")

                if self.id == "R1":
                    self.send_to_client(msg)
                else:
                    for client in self.clients:
                        client_conn = self.clients[client]
                        client_conn.send(msg.encode("utf-8"))

    def send_to_neighbors(self, msg):
        for ngh_addr in self.neighbors:
            conn = self.neighbors_conns[ngh_addr]
            conn.send(msg)

    def send_to_client(self, msg):
        msg = msg.split("@")
        msg_to_send = msg[0]
        client_address = msg[1]
        client_conn = self.clients[client_address]
        client_conn.send(msg_to_send.encode("utf-8"))

    def connect_to_neighbors(self):
        for i in range(len(self.neighbors)):
            addr = self.neighbors[i]
            self.neighbors_conns[addr] = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self.neighbors_conns[addr].connect(addr)
            threading.Thread(
                target=self.receive_from_a_neighbor,
                args=(self.neighbors_conns[addr], addr),
            ).start()

    def start_packet_capture(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        interface = r"\Device\NPF_Loopback"  # Use to loopback interface

        try:
            display_filter = f"tcp.port == {self.routers_ports[0]} or tcp.port == {self.routers_ports[1]} or tcp.port == {self.routers_ports[2]} or tcp.port == {self.routers_ports[3]}"
            capture = pyshark.LiveCapture(
                interface=interface, display_filter=display_filter
            )

            # Open file to write
            with open("wireshark.log", "a") as log_file:
                for packet in capture.sniff_continuously():
                    if "TCP" in packet and hasattr(packet.tcp, "payload"):
                        # Remove header from packet content
                        payload = packet.tcp.payload

                        # Convert hexadecimal content to string
                        hex_data_cleaned = payload.replace(":", "")
                        byte_data = bytes.fromhex(hex_data_cleaned)
                        string_data = byte_data.decode("utf-8", errors="ignore")

                        # # Write in terminal
                        # print(f"\nPacket content : {string_data}")
                        # print(f"Source Port: {packet.tcp.srcport}")
                        # print(f"Destination Port: {packet.tcp.dstport}\n")

                        # Write in file
                        log_file.write(f"\n*****Router {self.id}*****\n")
                        log_file.write(f"\nPacket content : {string_data}\n")
                        log_file.write(f"Source Port: {packet.tcp.srcport}\n")
                        log_file.write(f"Destination Port: {packet.tcp.dstport}\n")
                        log_file.flush()

        except Exception as e:
            print(f"[{self.id}] Traffic recording error: {e}")

    def start(self):
        self.connect_to_neighbors()

        # Create a socket to start the listener socket.
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(self.address)
        self.conn.listen(1)
        print(f"Listening on address {self.address} ...")

        # Start packet capture in a separate thread
        threading.Thread(target=self.start_packet_capture, daemon=True).start()

        while True:
            client_conn, client_addr = self.conn.accept()
            print(f"Connection established with {client_addr}")

            keys = pickle.dumps(self.all_keys)
            client_conn.send(keys)

            self.clients[f"{client_addr}"] = client_conn

            threading.Thread(
                target=self.send_to_server, args=(client_conn, client_addr)
            ).start()


if __name__ == "__main__":
    id = f"R{input("enter router id: ")}"

    base = 8000

    R1_port = base + 1
    R2_port = base + 2
    R3_port = base + 3
    R4_port = base + 4
    server_port = 9999

    # neighbor means server
    # R1_neighbors = [("127.0.0.1", R2_port), ("127.0.0.1", R4_port)]
    R1_neighbors = [("127.0.0.1", R2_port)]
    R2_neighbors = [("127.0.0.1", R3_port)]
    R3_neighbors = [("127.0.0.1", server_port)]
    R4_neighbors = [("127.0.0.1", R3_port)]

    if id == "R1":
        port = R1_port
        neighbors = R1_neighbors
    elif id == "R2":
        port = R2_port
        neighbors = R2_neighbors
    elif id == "R3":
        port = R3_port
        neighbors = R3_neighbors
    elif id == "R4":
        port = R4_port
        neighbors = R4_neighbors

    router = Router(id, ("127.0.0.1", port), neighbors)
    router.routers_ports = [R1_port, R2_port, R3_port, R4_port]
    router.start()
