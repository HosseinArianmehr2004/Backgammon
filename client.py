import socket
import threading

# from random import randint


class Client:
    def __init__(self, server_addr):
        self.address = None
        self.peer_address = None
        self.server_address = server_addr

        # conn is the socket that is created to a client(peer) can connect
        self.conn = None
        self.peer_conn = None
        self.server_conn = None

        self.options = [
            "\nOptions:",
            "1. Send message to the Server",
            "2. Send message to Peer",
            "3. Listen for peer connections",
            "4. Connect to one of the online clients",
            "5. Exit\n",
        ]

    def receive_message(self, conn, addr):
        while True:
            msg = conn.recv(1024).decode("utf-8")
            if not msg:
                break
            else:
                print(f"Received from {addr}: {msg}")

        conn.close()

    def send_message(self, conn, msg):
        conn.send(msg.encode("utf-8"))

    def start_client(self):
        self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_conn.connect(self.server_address)

        while True:
            for x in self.options:
                print(x)

            choice = input("Choose an option: ")

            if choice == "1":
                msg = input("Enter message to send to Server: ")
                self.send_message(self.server_conn, msg)

            elif choice == "2":
                msg = input("Enter the message to send to peer: ")
                self.send_message(self.peer_conn, msg)

            elif choice == "3":
                port = int(input("Enter port to listen for peer connections: "))

                self.address = "127.0.0.1", port
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.bind(self.address)
                self.conn.listen(1)
                print(f"Listening for peer connections on port {port}...")

                msg = f"ADD-{self.address}"
                self.send_message(self.server_conn, msg)

                self.peer_conn, self.peer_address = self.conn.accept()
                print(f"Connected to peer: {self.peer_address}")

                # Start a thread to handle incoming messages from the peer
                threading.Thread(
                    target=self.receive_message,
                    args=(self.peer_conn, self.peer_address),
                    daemon=True,
                ).start()

            elif choice == "4":
                # Request the list of online clients from the server
                self.send_message(self.server_conn, "GET_CLIENTS")

                online_clients = self.server_conn.recv(1024).decode("utf-8")
                print("Online clients:")
                print(online_clients)

                # self.peer_address = input("host: "), int(input("port: "))
                self.peer_address = "127.0.0.1", int(input("port: "))

                self.peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.peer_conn.connect(self.peer_address)
                print(f"Connected to {self.peer_address}")

                msg = f"REMOVE-{self.peer_address}"
                self.send_message(self.server_conn, msg)

                # Start a thread for the new client connection
                threading.Thread(
                    target=self.receive_message,
                    args=(self.peer_conn, self.peer_address),
                    daemon=True,
                ).start()

            elif choice == "5":
                print("Exiting...")
                self.conn.close()
                self.peer_conn.close()
                self.server_conn.close()
                break

            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    client = Client(("127.0.0.1", 9999))
    client.start_client()
