import socket
import threading


class Client:
    def __init__(self, server_addr):
        self.address = None
        self.server_address = server_addr
        self.peer_address = None

        self.conn = None
        self.peer_conn = None
        self.server_conn = None

    def receive_message(self, conn, addr):
        """Function to handle incoming messages from the connected client."""
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
            print("\nOptions:")
            print("1. Send message to the server")
            print("2. Connect to one of the online clients")
            print("3. Listen for peer connections")
            print("4. Send message to a specific address")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                msg = input("Enter message to send to Server: ")
                self.send_message(self.server_conn, msg)

            elif choice == "2":
                # Request the list of online clients from the server
                self.send_message(self.server_conn, "GET_CLIENTS")

                # online_clients = self.server_conn.recv(1024).decode("utf-8").split("\n")
                online_clients = self.server_conn.recv(1024).decode("utf-8")
                print("Online clients:")
                print(online_clients)

                # self.peer_address = input("host: "), int(input("port: "))
                self.peer_address = "127.0.0.1", int(input("port: "))

                self.peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.peer_conn.connect(self.peer_address)
                print(f"Connected to {self.peer_address}")

                # Start a thread for the new client connection
                threading.Thread(
                    target=self.receive_message,
                    args=(self.peer_conn, self.peer_address),
                    daemon=True,
                ).start()

                while True:
                    msg = input(
                        "Enter message to send to the online client (or 'exit' to disconnect): "
                    )
                    if msg.lower() == "exit":
                        self.peer_conn.close()
                        break
                    self.send_message(self.peer_conn, msg)

            elif choice == "3":
                port = int(input("Enter port to listen for peer connections: "))

                """Function to listen for incoming connections from peers."""
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.bind(("127.0.0.1", port))
                self.conn.listen(1)
                print(f"Listening for peer connections on port {port}...")

                self.peer_conn, self.peer_address = self.conn.accept()
                print(f"Connected to peer: {self.peer_address}")

                # Start a thread to handle incoming messages from the peer
                threading.Thread(
                    target=self.receive_message,
                    args=(self.peer_conn, self.peer_address),
                    daemon=True,
                ).start()

            elif choice == "4":
                msg = input("Enter the message to send to peer: ")
                self.send_message(self.peer_conn, msg)

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
