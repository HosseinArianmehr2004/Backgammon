import socket
import pickle
import random
import pyshark
import asyncio
import threading
from cryptography.fernet import Fernet


class Server:
    def __init__(self, addr):
        self.address = addr
        self.conn = None
        self.clients = set()
        self.keys = self.generate_keys(4)

    def receive_message(self, conn, addr):
        while True:
            message_received = conn.recv(1024).decode("utf-8").split("@")
            print(message_received)
            msg = message_received[0]
            client_address = message_received[1]
            # msg = self.decrypt_data(message_received[0].encode("utf-8")).decode("utf-8")
            msg = msg.split(":")

            if msg[0] == "ADD":  # add a new online client address to self.clients
                online_client_address = msg[1]
                self.clients.add(online_client_address)

            elif msg[0] == "REMOVE":  # remove address(msg[1]) from self.clients
                address = msg[1]
                # self.clients.remove(address)

            elif msg[0] == "GET_CLIENTS":
                online_clients = "\n".join([str(x) for x in self.clients])
                msg_to_send = f"{online_clients}@{client_address}"
                conn.send(msg_to_send.encode("utf-8"))

            elif msg[0] == "DICE":
                value_1 = random.randint(1, 6)
                value_2 = random.randint(1, 6)
                msg_to_send = f"DICE:{value_1}:{value_2}@{client_address}"
                conn.send(msg_to_send.encode("utf-8"))

            else:
                print(f"{msg} is not a command !\n")

    def send_message(self, conn):
        while True:
            msg = input("Enter message (or 'exit' to quit): ")
            if msg.lower() == "exit":
                break
            conn.send(msg.encode("utf-8"))

        conn.close()

    def decrypt_data(self, decrypted_data):
        for key in reversed(self.keys):
            cipher = Fernet(key)
            decrypted_data = cipher.decrypt(decrypted_data)
        return decrypted_data

    def generate_keys(self, num_keys):
        keys = []
        for _ in range(num_keys):
            key = Fernet.generate_key()
            keys.append(key)
        return keys

    def start_packet_capture(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        interface = r"\Device\NPF_Loopback"  # Use to loopback interface

        try:
            capture = pyshark.LiveCapture(
                interface=interface, display_filter="tcp.port == 9988"
            )
            print(f"\nin server start recording network traffic !\n")

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

                        # Write in terminal
                        print(f"\nPacket content : {string_data}")
                        print(f"Source Port: {packet.tcp.srcport}")
                        print(f"Destination Port: {packet.tcp.dstport}\n")

                        # Write in file
                        log_file.write(f"\n*****Server*****\n")
                        log_file.write(f"Packet content : {string_data}\n")
                        log_file.write(f"Source Port: {packet.tcp.srcport}\n")
                        log_file.write(f"Destination Port: {packet.tcp.dstport}\n")
                        log_file.flush()

        except Exception as e:
            print(f"Traffic recording error: {e}")

    def start(self):
        """Function to start the listener socket."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(self.address)
        self.conn.listen(1)
        print(f"Listening on address {self.address} ...")

        # Start packet capture in a separate thread
        # threading.Thread(target=self.start_packet_capture, daemon=True).start()

        while True:
            router_conn, addr = self.conn.accept()
            print(f"Connection established with {addr}")
            for key in self.keys:
                print(key)
            keys = pickle.dumps(self.keys)
            router_conn.send(keys)
            # self.clients.add(addr)

            threading.Thread(
                target=self.receive_message, args=(router_conn, addr)
            ).start()
            # threading.Thread(target=self.send_message, args=(client_conn,)).start()

        self.conn.close()


if __name__ == "__main__":
    server = Server(("127.0.0.1", 9999))
    server.start()
