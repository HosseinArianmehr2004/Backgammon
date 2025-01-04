import tkinter as tk
import socket
import threading


class MessageApp:
    def __init__(self, root, conn):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x500")
        self.root.configure(bg="#f0f0f0")

        # Create a title label
        title_label = tk.Label(
            self.root, text="Chat Application", font=("Helvetica", 16), bg="#f0f0f0"
        )
        title_label.pack(pady=10)

        # Create a frame for the output and input
        self.frame = tk.Frame(self.root, bg="#ffffff")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Text area for displaying messages
        self.text_area = tk.Text(
            self.frame, wrap=tk.WORD, bg="#eaeaea", font=("Helvetica", 12)
        )
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Entry box for user input
        self.input_box = tk.Entry(self.frame, font=("Helvetica", 12), bg="#ffffff")
        self.input_box.pack(fill=tk.X, padx=10, pady=10)
        self.input_box.bind(
            "<Return>", lambda event: self.send_message_chat(conn)
        )  # Bind Enter key to send message

        # Start a thread to listen for incoming messages
        threading.Thread(target=self.receive_message, args=(conn,), daemon=True).start()

    def display_message(self, message):
        self.text_area.insert(tk.END, message + "\n")  # Add message to text area

    def send_message_chat(self, conn):
        user_input = self.input_box.get()
        if user_input:
            msg = f"CHAT:{user_input}"
            conn.send(msg.encode("utf-8"))  # Send message to the other peer
            self.display_message(f"You: {user_input}")  # Display message in text area
            self.input_box.delete(0, tk.END)  # Clear input box

    def receive_message(self, conn):
        while True:
            try:
                msg = conn.recv(1024).decode("utf-8")
                if not msg:
                    break
                else:
                    msg = msg.split(":")
                    if msg[0] == "CHAT":
                        self.display_message(f"Opponent: {msg[1]}")
            except:
                break


# Function to start the client
def start_client(conn):
    # conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # conn.connect(("127.0.0.1", 9090))  # Connect to the server
    root = tk.Tk()
    app = MessageApp(root, conn)
    root.mainloop()


# Start the client
# start_client()
