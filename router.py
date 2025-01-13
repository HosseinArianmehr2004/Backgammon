import socket
import pyshark
import asyncio
import threading

# from cryptography.fernet import Fernet


class Router:
    def __init__(self, address, server_address):
        self.address = address
        self.server_address = server_address

        self.conn = None
        self.server_conn = None

        self.clients = {}

    def send_to_server(self, client_conn, client_addr):
        while True:
            msg = client_conn.recv(1024).decode("utf-8")
            if msg:
                msg_to_send = f"{msg}@{client_addr}"
                print(f"msg_to_send: {msg_to_send}")
                self.server_conn.send(msg_to_send.encode("utf-8"))

    def receive_message_from_server(self):
        while True:
            msg_received = self.server_conn.recv(1024).decode("utf-8").split("@")
            print(f"msg_received : {msg_received}")

            msg = msg_received[0]
            client_address = msg_received[1]
            client_conn = self.clients[client_address]

            client_conn.send(msg.encode("utf-8"))

    def start_packet_capture(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        interface = r"\Device\NPF_Loopback"  # Use to loopback interface

        try:
            capture = pyshark.LiveCapture(
                interface=interface, display_filter="tcp.port == 8888"
            )
            print(f"\nStart recording network traffic !\n")

            for packet in capture.sniff_continuously():
                if "TCP" in packet and hasattr(packet.tcp, "payload"):
                    # Remove header from packet content
                    payload = packet.tcp.payload

                    # Convert hexadecimal content to string
                    hex_data_cleaned = payload.replace(":", "")
                    byte_data = bytes.fromhex(hex_data_cleaned)
                    string_data = byte_data.decode("utf-8", errors="ignore")

                    # Print packet content
                    print(f"\nPacket content : {string_data}")
                    print(f"Source Port: {packet.tcp.srcport}")
                    print(f"Destination Port: {packet.tcp.dstport}\n")

        except Exception as e:
            print(f"Traffic recording error: {e}")

    def start(self):
        # Create a socket to connect to the server
        self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_conn.connect(self.server_address)  # Connect to the server

        threading.Thread(target=self.receive_message_from_server, args=()).start()

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

            self.clients[f"{client_addr}"] = client_conn

            threading.Thread(
                target=self.send_to_server, args=(client_conn, client_addr)
            ).start()

        self.conn.close()


if __name__ == "__main__":
    router = Router(("127.0.0.1", 8888), ("127.0.0.1", 9999))
    router.start()
