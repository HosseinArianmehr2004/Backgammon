import socket
import threading
from Backgammon_Game import Player

# from cryptography.fernet import Fernet


class Client:
    def __init__(self, server_addr):
        self.game_address = None
        self.game_peer_address = None
        self.router_address = server_addr

        self.game_conn = None
        self.game_peer_conn = None
        self.router_conn = None

        self.options = [
            "\nOptions:",
            "1. Send message to server",
            "2. Create game room",
            "3. Join a game",
            "4. Exit\n",
        ]

    def run_game(self, color):
        # Run the game in a separate thread
        player = Player(self.game_conn, self.game_peer_conn, color, self.router_conn)
        # player = Player(self.game_conn, self.game_peer_conn, color)
        threading.Thread(
            target=player.main,
            args=(),
            daemon=True,
        ).start()

    def send_message(self, conn, msg):
        conn.send(msg.encode("utf-8"))

    def start(self):
        self.router_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.router_conn.connect(self.router_address)

        while True:
            for x in self.options:
                print(x)

            choice = input("Choose an option : ")

            if choice == "1":
                msg = input("Enter message to send to Server : ")
                self.send_message(self.router_conn, msg)

            elif choice == "2":
                # port = int(input("Enter port to listen for peer connections: "))
                port = 12345

                self.game_address = "127.0.0.1", port
                self.game_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.game_conn.bind(self.game_address)
                self.game_conn.listen(1)
                print(f"Listening for peer connections on port {port} ...")

                msg = f"ADD:{self.game_address}"
                self.send_message(self.router_conn, msg)

                self.game_peer_conn, self.game_peer_address = self.game_conn.accept()
                print(f"Connected to peer : {self.game_peer_address}")

                print("Starting the game ...")
                self.run_game("white")

            elif choice == "3":
                # Request the list of online clients from the server
                self.send_message(self.router_conn, "GET_CLIENTS")

                online_clients = self.router_conn.recv(1024).decode("utf-8")

                print("Online clients:")
                print(online_clients)

                # self.peer_address = input("host: "), int(input("port: "))
                self.game_peer_address = "127.0.0.1", 12345

                self.game_peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.game_peer_conn.connect(self.game_peer_address)
                print(f"Connected to {self.game_peer_address}")

                msg = f"REMOVE:{self.game_peer_address}"
                self.send_message(self.router_conn, msg)

                print("Starting the game ...")
                self.run_game("black")

            elif choice == "4":  # Updated exit option
                print("Exiting ...")

                if self.game_conn:
                    self.game_conn.close()
                if self.game_peer_conn:
                    self.game_peer_conn.close()
                if self.router_conn:
                    self.router_conn.close()
                break

            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    client = Client(("127.0.0.1", 8888))
    client.start()
