import socket
import threading
from Backgammon_Game import Player
from cryptography.fernet import Fernet


class Client:
    def __init__(self, server_addr):
        self.chat_address = None
        self.game_address = None
        self.chat_peer_address = None
        self.game_peer_address = None
        self.server_address = server_addr

        # conn is the socket that is created to a client(peer) can connect
        self.chat_conn = None
        self.game_conn = None
        self.chat_peer_conn = None
        self.game_peer_conn = None
        self.server_conn = None

        self.options = [
            "\nOptions:",
            "1. Send message to the Server",
            "2. Send message to Peer",
            "3. (CHAT) Listen for peer connections",
            "4. (CHAT) Connect to one of the online clients",
            "5. (GAME) Listen for peer connections",
            "6. (GAME) Connect to one of the online clients",
            "7. Exit\n",
        ]

        # For cryptography
        self.cipher_suite = None

    def run_game(self, color):
        # Run the game in a separate thread
        player = Player(self.game_conn, self.game_peer_conn, color)
        threading.Thread(
            target=player.main,
            args=(),
            daemon=True,
        ).start()

    def receive_message(self, conn, addr):
        while True:
            encrypted_msg = conn.recv(1024)
            if not encrypted_msg:
                break
            else:
                try:
                    msg = self.cipher_suite.decrypt(encrypted_msg).decode("utf-8")
                    print(f"Received from {addr}:\n{msg}")
                except Exception as e:
                    print(f"Error decrypting message: {e}")

        conn.close()

    def send_message(self, conn, msg):
        encrypted_msg = self.cipher_suite.encrypt(msg.encode("utf-8"))
        conn.send(encrypted_msg)

    def start_client(self):
        self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_conn.connect(self.server_address)

        # Receive key from server
        self.key = self.server_conn.recv(1024)
        self.cipher_suite = Fernet(self.key)

        while True:
            for x in self.options:
                print(x)

            choice = input("Choose an option: ")

            if choice == "1":
                msg = input("Enter message to send to Server: ")
                self.send_message(self.server_conn, msg)

            elif choice == "2":
                msg = input("Enter the message to send to peer: ")
                self.send_message(self.chat_peer_conn, msg)

            elif choice == "3":
                port = int(input("Enter port to listen for peer connections: "))

                self.chat_address = "127.0.0.1", port
                self.chat_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.chat_conn.bind(self.chat_address)
                self.chat_conn.listen(1)
                print(f"Listening for peer connections on port {port}...")

                msg = f"ADD-{self.chat_address}"
                self.send_message(self.server_conn, msg)

                self.chat_peer_conn, self.chat_peer_address = self.chat_conn.accept()
                print(f"Connected to peer: {self.chat_peer_address}")

                # Start a thread to handle incoming messages from the peer
                threading.Thread(
                    target=self.receive_message,
                    args=(self.chat_peer_conn, self.chat_peer_address),
                    daemon=True,
                ).start()

            elif choice == "4":
                # Request the list of online clients from the server
                self.send_message(self.server_conn, "GET_CLIENTS")

                # online_clients = self.server_conn.recv(1024).decode("utf-8")
                online_clients = self.server_conn.recv(1024)
                online_clients = self.cipher_suite.decrypt(online_clients).decode(
                    "utf-8"
                )
                print("Online clients:")
                print(online_clients)

                # self.peer_address = input("host: "), int(input("port: "))
                self.chat_peer_address = "127.0.0.1", int(input("port: "))

                self.chat_peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.chat_peer_conn.connect(self.chat_peer_address)
                print(f"Connected to {self.chat_peer_address}")

                msg = f"REMOVE-{self.chat_peer_address}"
                self.send_message(self.server_conn, msg)

                # Start a thread for the new client connection
                threading.Thread(
                    target=self.receive_message,
                    args=(self.chat_peer_conn, self.chat_peer_address),
                    daemon=True,
                ).start()

            elif choice == "5":
                port = int(input("Enter port to listen for peer connections: "))

                self.game_address = "127.0.0.1", port
                self.game_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.game_conn.bind(self.game_address)
                self.game_conn.listen(1)
                print(f"Listening for peer connections on port {port}...")

                msg = f"ADD-{self.game_address}"
                self.send_message(self.server_conn, msg)

                self.game_peer_conn, self.game_peer_address = self.game_conn.accept()
                print(f"Connected to peer: {self.game_peer_address}")

                print("Starting the game...")
                self.run_game("white")

            elif choice == "6":
                # Request the list of online clients from the server
                self.send_message(self.server_conn, "GET_CLIENTS")

                # online_clients = self.server_conn.recv(1024).decode("utf-8")
                online_clients = self.server_conn.recv(1024)
                online_clients = self.cipher_suite.decrypt(online_clients).decode(
                    "utf-8"
                )
                print("Online clients:")
                print(online_clients)

                # self.peer_address = input("host: "), int(input("port: "))
                self.game_peer_address = "127.0.0.1", int(input("port: "))

                self.game_peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.game_peer_conn.connect(self.game_peer_address)
                print(f"Connected to {self.game_peer_address}")

                msg = f"REMOVE-{self.game_peer_address}"
                self.send_message(self.server_conn, msg)

                print("Starting the game...")
                self.run_game("black")

            elif choice == "7":  # Updated exit option
                print("Exiting...")
                if self.chat_conn:
                    self.chat_conn.close()
                if self.game_conn:
                    self.game_conn.close()
                if self.chat_peer_conn:
                    self.chat_peer_conn.close()
                if self.game_peer_conn:
                    self.game_peer_conn.close()
                if self.server_conn:
                    self.server_conn.close()
                break

            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    client = Client(("127.0.0.1", 9090))
    client.start_client()
