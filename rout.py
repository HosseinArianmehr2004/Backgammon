import socket
import threading

# from cryptography.fernet import Fernet


class Router:
    def __init__(self, id, address, neighbors_addresses):
        self.id = id
        self.address = address
        self.conn = None

        self.neighbors = neighbors_addresses

        self.neighbors_conns = {}
        for ngh_addr in neighbors_addresses:
            self.neighbors_conns[ngh_addr] = None

        self.clients = {}  # this is just for router 1

    def send_to_server(self, conn, addr):
        while True:
            print(f"in (send_to_server) method with args = {addr}")
            msg = conn.recv(1024).decode("utf-8")

            if self.id == "R1":
                msg = f"{msg}@{addr}"

            print(f"msg to send: {msg}")

            self.send_to_neighbors(msg)

            # self.server_conn.send(msg.encode("utf-8"))

    # actualy receive from server
    def receive_from_a_neighbor(self, ngh_conn, ngh_addr):
        while True:
            print(f"in (send_to_server) method with args = {ngh_addr}")
            msg = ngh_conn.recv(1024).decode("utf-8")
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
            conn.send(msg.encode("utf-8"))

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

    def start(self):
        self.connect_to_neighbors()

        # Create a socket to start the listener socket.
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(self.address)
        self.conn.listen(1)
        print(f"Listening on address {self.address} ...")

        while True:
            client_conn, client_addr = self.conn.accept()
            print(f"Connection established with {client_addr}")

            self.clients[f"{client_addr}"] = client_conn

            threading.Thread(
                target=self.send_to_server, args=(client_conn, client_addr)
            ).start()

        self.conn.close()


if __name__ == "__main__":
    id = f"R{input("enter id: ")}"

    base = 7500

    R1_port = base + 1
    R2_port = base + 2
    R3_port = base + 3
    R4_port = base + 4
    server_port = 9988

    # neighbor means server
    R1_neighbors = [("127.0.0.1", R2_port), ("127.0.0.1", R3_port)]
    R2_neighbors = [("127.0.0.1", R4_port)]
    R3_neighbors = [("127.0.0.1", R4_port)]
    R4_neighbors = [("127.0.0.1", server_port)]

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
    router.start()
