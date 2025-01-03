import socket
import threading


# class Server(DatagramProtocol):
#     def __init__(self):
#         self.clients = set()

#     def datagramReceived(self, datagram, addr):
#         datagram = datagram.decode("utf-8")
#         if datagram == "ready":
#             addresses = "\n".join([str(x) for x in self.clients])
#             self.transport.write(addresses.encode("utf-8"), addr)
#             self.clients.add(addr)


clients = set()


def receive_message(conn, addr):
    """Function to handle incoming messages from the connected client."""
    while True:
        msg = conn.recv(1024).decode("utf-8")
        if not msg:
            break
        elif msg == "ready":
            addresses = "\n".join([str(x) for x in clients])
            conn.send(addresses.encode("utf-8"))
            # clients.add(addr)
        elif msg == "GET_CLIENTS":
            # Handle the GET_CLIENTS request
            addresses = "\n".join([str(x) for x in clients])
            conn.send(addresses.encode("utf-8"))
        else:
            print(f"Received from {addr}: {msg}")

    conn.close()


def send_message(conn):
    # Main thread for sending messages
    while True:
        msg = input("Enter message (or 'exit' to quit): ")
        if msg.lower() == "exit":
            break
        conn.send(msg.encode("utf-8"))

    conn.close()


def start_listener(host, port):
    """Function to start the listener socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((host, port))
    listener.listen(1)
    print(f"Listening on port {port}...")

    while True:
        conn, addr = listener.accept()
        print(f"Connection established with {addr}")

        clients.add(addr)

        # Start a thread to handle incoming messages
        threading.Thread(target=receive_message, args=(conn, addr)).start()
        # threading.Thread(target=send_message, args=(conn,)).start()

    listener.close()


if __name__ == "__main__":
    start_listener("127.0.0.1", 9999)
