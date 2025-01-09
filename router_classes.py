import socket
import threading


class Router_1:
    def __init__(self, address, server_address):
        self.address = address
        self.server_address = server_address

        self.conn = None
        self.server_conn = None

        self.clients = {}
        self.neighbors = []

    def add_neighbors(self, neighbors):
        self.neighbors = neighbors

    def send_msg_to_neighbors(self, msg):
        for neighbor in self.neighbors:
            neighbor.receive(msg, self)

    def receive(self, msg, ignore_neighbor=None):
        print(f"r1 receive message: {msg}")
        msg = msg.split("@")

        message_to_send = msg[0]
        client_address = msg[1]

        client_conn = self.clients[client_address]
        client_conn.send(message_to_send.encode("utf-8"))

    def receive_message_from_clients(self, client_conn, client_addr):
        while True:
            msg = client_conn.recv(1024).decode("utf-8")
            if msg:
                msg_to_send = f"{msg}@{client_addr}"
                print(f"r1 receive message: {msg_to_send}")
                self.send_msg_to_neighbors(msg_to_send)
                # self.server_conn.send(msg_to_send.encode("utf-8"))

    # def receive_message_from_server(self):
    #     while True:
    #         msg_received = self.server_conn.recv(1024).decode("utf-8").split("@")
    #         print(f"msg received from server: {msg_received}")

    #         msg = msg_received[0]
    #         client_address = msg_received[1]
    #         client_conn = self.clients[client_address]

    #         client_conn.send(msg.encode("utf-8"))

    def start(self):
        # # Create a socket to connect to the server
        # self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_conn.connect(self.server_address)  # Connect to the server

        # threading.Thread(target=self.receive_message_from_server, args=()).start()

        # Create a socket to start the listener socket.
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(self.address)
        self.conn.listen(1)
        print(f"Listening on address {self.address}...")

        while True:
            client_conn, client_addr = self.conn.accept()
            print(f"Connection established with {client_addr}")

            self.clients[f"{client_addr}"] = client_conn

            threading.Thread(
                target=self.receive_message_from_clients,
                args=(client_conn, client_addr),
            ).start()

        self.conn.close()


class Router_Miani:
    def __init__(self, name):
        self.name = name
        self.neighbors = []

    def add_neighbors(self, neighbors):
        self.neighbors = neighbors

    def send(self, msg, ignore_neighbor):
        for neighbor in self.neighbors:
            if neighbor != ignore_neighbor:
                neighbor.receive(msg, self)

    def receive(self, msg, ignore_neighbor):
        print(f"{self.name} receive message: {msg}")
        self.send(msg, ignore_neighbor)


class Router_n:
    def __init__(self, address, server_address):
        self.address = address
        self.server_address = server_address

        self.conn = None
        self.server_conn = None

        self.clients = {}
        self.neighbors = []

    def add_neighbors(self, neighbors):
        self.neighbors = neighbors

    def send_msg_to_neighbors(self, msg):
        for neighbor in self.neighbors:
            neighbor.receive(msg, self)

    def receive(self, msg, ignore_neighbor=None):
        print(f"rn receive message: {msg}")
        self.server_conn.send(msg.encode("utf-8"))

    # def receive_message_from_clients(self, client_conn, client_addr):
    #     while True:
    #         msg = client_conn.recv(1024).decode("utf-8")
    #         if msg:
    #             msg_to_send = f"{msg}@{client_addr}"
    #             print(f"msg_to_send: {msg_to_send}")
    #             self.send_msg_to_neighbors(msg_to_send.encode("utf-8"))
    #             # self.server_conn.send(msg_to_send.encode("utf-8"))

    def receive_message_from_server(self):
        while True:
            message_received = self.server_conn.recv(1024).decode("utf-8")
            if message_received:
                print(f"message_received: {message_received}\n")
                # msg, client_address = message_received.split("@")
                # client_conn = self.clients[client_address]
                # client_conn.send(msg.encode("utf-8"))
                self.send_msg_to_neighbors(message_received)

    def start(self):
        # Create a socket to connect to the server
        self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_conn.connect(self.server_address)  # Connect to the server

        self.receive_message_from_server()

        # threading.Thread(target=self.receive_message_from_server, args=()).start()

        # # Create a socket to start the listener socket.
        # self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn.bind(self.address)
        # self.conn.listen(1)
        # print(f"Listening on address {self.address}...")

        # while True:
        #     client_conn, client_addr = self.conn.accept()
        #     print(f"Connection established with {client_addr}")

        #     self.clients[f"{client_addr}"] = client_conn

        #     threading.Thread(
        #         target=self.receive_message_from_clients, args=(client_conn, client_addr)
        #     ).start()

        # self.conn.close()


if __name__ == "__main__":
    r1 = Router_1(("127.0.0.1", 8888), None)
    r2 = Router_Miani("r2")
    r3 = Router_Miani("r3")
    r4 = Router_Miani("r4")
    # r5 = Router_Miani("r5")
    rn = Router_n(None, ("127.0.0.1", 9999))

    r1.add_neighbors([r2, r3])
    r2.add_neighbors([r1, r4])
    r3.add_neighbors([r1, rn])
    r4.add_neighbors([r2, rn])
    # r5.add_neighbors([r2, rn])
    rn.add_neighbors([r3, r4])

    threading.Thread(target=r1.start).start()
    threading.Thread(target=rn.start).start()
