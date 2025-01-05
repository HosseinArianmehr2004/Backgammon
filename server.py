import random
import socket
import threading
from cryptography.fernet import Fernet


class Server:
    def __init__(self, addr):
        self.address = addr
        self.conn = None
        self.clients = set()

        # For cryptography
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def receive_message(self, conn, addr):
        while True:
            encrypted_msg = conn.recv(1024)
            if not encrypted_msg:
                break

            try:
                msg = self.cipher_suite.decrypt(encrypted_msg).decode("utf-8")
                msg = msg.split("-")

                if msg[0] == "ADD":  # add a new online client address to self.clients
                    online_client_address = msg[1]
                    self.clients.add(online_client_address)

                elif msg[0] == "REMOVE":  # remove address(msg[1]) from self.clients
                    address = msg[1]
                    self.clients.remove(address)

                elif msg[0] == "GET_CLIENTS":
                    addresses = "\n".join([str(x) for x in self.clients])
                    conn.send(self.cipher_suite.encrypt(addresses.encode("utf-8")))

                elif msg[0] == "DICE":
                    value_1 = random.randint(1, 6)
                    value_2 = random.randint(1, 6)
                    msg = f"DICE:{value_1}:{value_2}"
                    # print(msg)
                    conn.send(self.cipher_suite.encrypt(msg.encode("utf-8")))

                else:
                    print(f"Received from {addr}: {msg}")

            except Exception as e:
                print(f"Error decrypting message: {e}")

        conn.close()

    def send_message(self, conn):
        while True:
            msg = input("Enter message (or 'exit' to quit): ")
            if msg.lower() == "exit":
                break
            encrypted_msg = self.cipher_suite.encrypt(msg.encode("utf-8"))
            conn.send(encrypted_msg)

        conn.close()

    def start(self):
        """Function to start the listener socket."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(self.address)
        self.conn.listen(1)
        print(f"Listening on address {self.address}...")

        while True:
            client_conn, addr = self.conn.accept()
            print(f"Connection established with {addr}")

            # Send key to client
            client_conn.send(self.key)

            threading.Thread(
                target=self.receive_message, args=(client_conn, addr)
            ).start()
            # threading.Thread(target=self.send_message, args=(client_conn,)).start()

        self.conn.close()


if __name__ == "__main__":
    server = Server(("127.0.0.1", 9090))
    server.start()
