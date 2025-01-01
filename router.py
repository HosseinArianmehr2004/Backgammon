from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class Router(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.server_address = ("127.0.0.1", 9999)

    def datagramReceived(self, datagram, addr):
        datagram = datagram.decode("utf-8")

        # If the message is from a client
        if addr in self.clients:
            print(f"Forwarding message from {addr} to server: {datagram}")
            self.transport.write(datagram.encode("utf-8"), self.server_address)

        # If the message is from the server
        elif addr == self.server_address:
            print(f"Received from server: {datagram}")
            # Forward it to all clients
            for client in self.clients:
                self.transport.write(datagram.encode("utf-8"), client)

        # If a new client is connecting
        else:
            if datagram == "ready":
                print(f"New client connected: {addr}")
                self.clients.add(addr)
                # Send the list of connected clients to the new client
                addresses = "\n".join([str(x) for x in self.clients])
                self.transport.write(addresses.encode("utf-8"), addr)


if __name__ == "__main__":
    reactor.listenUDP(8888, Router())  # Router listens on port 8888
    reactor.run()
