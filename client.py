from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import socket
import threading


class Client(DatagramProtocol):
    def __init__(self, host, port):
        if host == "localhost":
            host = "127.0.0.1"

        self.address = None
        self.id = host, port
        self.server = "127.0.0.1", 9999
        print("Working on id: ", self.id)

    def startProtocol(self):
        self.transport.write("ready".encode("utf-8"), self.server)

    def datagramReceived(self, datagram, addr):
        datagram = datagram.decode("utf-8")

        if addr == self.server:
            print("Choose a client from these:\n", datagram)
            self.address = input("Write host: "), int(input("Write port: "))
            reactor.callInThread(self.send_message)
        else:
            print(addr, ":", datagram)

    def send_message(self):
        while True:
            self.transport.write(input(":::").encode("utf-8"), self.address)


def handle_connection(conn):
    """Function to handle incoming messages from the connected client."""
    while True:
        msg = conn.recv(1024).decode("utf-8")
        if not msg:
            break
        print(f"Received: {msg}")
    conn.close()


def start_client(remote_host, remote_port):
    """Function to start the client socket."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((remote_host, remote_port))
    client.send("ready".encode("utf-8"))

    # Start a thread to handle incoming messages
    threading.Thread(target=handle_connection, args=(client,)).start()

    # Main thread for sending messages
    while True:
        msg = input("Enter message (or 'exit' to quit): ")
        if msg.lower() == "exit":
            break
        client.send(msg.encode("utf-8"))

    client.close()


if __name__ == "__main__":
    # remote_host = input("Enter remote host: ")
    # remote_port = int(input("Enter remote port: "))
    # start_client(remote_host, remote_port)
    start_client("127.0.0.1", 9090)

    # port = randint(1000, 5000)
    # reactor.listenUDP(port, Client("localhost", port))
    # reactor.run()
