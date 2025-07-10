#chat_Server.py
import socket
import threading
import json
from typing import Dict
import sys
import os

class ChatServer:
    def __init__(self, host: str = 'localhost', port: int = 5000, log_file: str = 'chat_log.json'):
        """Initialize the chat server with the specified host, port, and log file."""
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[str, socket.socket] = {}  # Maps username to socket
        self.clients_lock = threading.Lock()
        self.server_running = True
        self.chat_log_file = log_file
        
        # Initialize or load the chat log file (if it doesn't exist, create it)
        if not os.path.exists(self.chat_log_file):
            with open(self.chat_log_file, 'w') as f:
                json.dump([], f)
        
    def start(self):
        """Start the server and begin accepting client connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        
        # Start listening for server commands (e.g., to shut down)
        command_thread = threading.Thread(target=self.listen_for_commands)
        command_thread.daemon = True
        command_thread.start()
        
        # Keep accepting new clients while the server is running
        while self.server_running:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            
            # Start a new thread to handle this client
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()
    
    def handle_client(self, client_socket: socket.socket):
        """Handle individual client connections and messages."""
        try:
            # Receive the first message containing the username
            username = json.loads(client_socket.recv(1024).decode())['username']
            
            # Ensure that the username is unique
            with self.clients_lock:
                if username in self.clients:
                    error_msg = json.dumps({"error": "Username already taken"})
                    client_socket.send(error_msg.encode())
                    client_socket.close()
                    return
                
                # Add the new client to the list of connected clients
                self.clients[username] = client_socket
                welcome_msg = json.dumps({"system": f"Welcome {username}!"})
                client_socket.send(welcome_msg.encode())
            
            while True:
                try:
                    # Receive the message sent by the client
                    message = json.loads(client_socket.recv(1024).decode())
                    
                    if not message:  # This means the client has disconnected unexpectedly
                        print(f"{username} has disconnected unexpectedly.")
                        break
                    
                    # Handle chat request or message type
                    if message.get('type') == 'chat_request':
                        target_user = message.get('target_user')
                        if target_user in self.clients:
                            response = json.dumps({
                                "system": f"Chat started with {target_user}"
                            })
                            client_socket.send(response.encode())
                        else:
                            error = json.dumps({
                                "error": f"User {target_user} not found"
                            })
                            client_socket.send(error.encode())
                    
                    elif message.get('type') == 'message':
                        target_user = message.get('target_user')
                        content = message.get('content')
                        
                        # If the target user exists, send the message to that user
                        if target_user in self.clients:
                            msg = json.dumps({
                                "from": username,
                                "content": content
                            })
                            self.clients[target_user].send(msg.encode())
                            self.log_message(username, target_user, content)  # Log the message
                        else:
                            error = json.dumps({
                                "error": f"User {target_user} not found"
                            })
                            client_socket.send(error.encode())
                
                except (json.JSONDecodeError, socket.error):
                    print(f"Error receiving data from {username}")
                    break
                
        except Exception as e:
            print(f"Error handling client {username}: {str(e)}")
        finally:
            # Clean up and remove the client from the list when they disconnect
            with self.clients_lock:
                if username in self.clients:
                    del self.clients[username]
            client_socket.close()

    def listen_for_commands(self):
        """Listen for server commands (e.g., '/quit' or '/help') to stop the server or show help."""
        while self.server_running:
            command = input("Enter '/quit' to stop the server or '/help' for instructions: ")
            if command == "/quit":
                self.shutdown_server()
            elif command == "/help":
                self.show_help()

    def show_help(self):
        """Show the available server commands."""
        print("Available Commands:\n/quit  - Quits and shuts down the server.\n/help  - Displays this help message.") 
       

    def shutdown_server(self):
        """Shutdown the server gracefully."""
        print("Shutting down the server...")
        self.server_running = False
        self.server_socket.close()
        sys.exit(0)

    def log_message(self, from_user: str, to_user: str, content: str):
        """Log the chat message to a JSON file."""
        chat_entry = {
            "from": from_user,
            "to": to_user,
            "content": content,
            "timestamp": self.get_timestamp()
        }
        
        # Read the current log
        with open(self.chat_log_file, 'r') as f:
            chat_log = json.load(f)
        
        # Add the new message to the log
        chat_log.append(chat_entry)
        
        # Write the updated log back to the file
        with open(self.chat_log_file, 'w') as f:
            json.dump(chat_log, f, indent=4)

    def get_timestamp(self):
        """Generate the current timestamp in a readable format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
if __name__ == "__main__":
    server = ChatServer()
    server.start()
