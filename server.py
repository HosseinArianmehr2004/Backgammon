import socket
import threading


class Server:
    def __init__(self, addr):
        self.address = addr
        self.conn = None
        self.clients = set()

    def receive_message(self, conn, addr):
        while True:
            msg = conn.recv(1024).decode("utf-8")

            if not msg:
                break

            else:
                msg = msg.split("-")

                if msg[0] == "ADD":  # add a new online client address to self.clients
                    online_client_address = msg[1]
                    self.clients.add(online_client_address)

                elif msg[0] == "REMOVE":  # remove address(msg[1]) from self.clients
                    address = msg[1]
                    self.clients.remove(address)

                elif msg[0] == "GET_CLIENTS":
                    addresses = "\n".join([str(x) for x in self.clients])
                    conn.send(addresses.encode("utf-8"))

                else:
                    print(f"Received from {addr}: {msg}")

        conn.close()

    def send_message(self, conn):
        while True:
            msg = input("Enter message (or 'exit' to quit): ")
            if msg.lower() == "exit":
                break
            conn.send(msg.encode("utf-8"))

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
            # self.clients.add(addr)

            threading.Thread(
                target=self.receive_message, args=(client_conn, addr)
            ).start()
            # threading.Thread(target=self.send_message, args=(client_conn,)).start()

        self.conn.close()


if __name__ == "__main__":
    server = Server(("127.0.0.1", 9090))
    server.start()
