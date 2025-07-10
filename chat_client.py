#chat_Client.py

"""מגישים: 1. אושרי הלוי ת"ז 318830569    אוראל כהן ת"ז 214266819"""

import socket
import threading
import json
import sys

class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 5000):
        """Initialize the chat client with the server's host and port."""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        
    def start(self):
        """Start the chat client and establish a connection to the server."""
        try:
            self.socket.connect((self.host, self.port))  # Connect to the server
        except ConnectionRefusedError:
            print("Could not connect to server. Is it running?")
            sys.exit(1)
            
        # Ask the user for a username and send it to the server
        self.username = input("Enter your username: ")
        self.send_message({
            "username": self.username
        })
        
        # Start a separate thread to listen for incoming messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Start the main command loop to handle user input
        self.command_loop()
    
    def command_loop(self):
        """Main loop to handle user commands such as chatting or messaging."""
        print("\nCommands:")
        print("/chat <username> - Start chat with user")
        print("/message <username> <message> - Send message to user")
        print("/quit - Exit the chat")
        
        while True:
            try:
                command = input()  # Get the user input for the command
                if command.startswith('/quit'):
                    break
                elif command.startswith('/chat'):  # Handle chat request
                    target_user = command.split()[1]
                    self.send_message({
                        "type": "chat_request",
                        "target_user": target_user
                    })
                elif command.startswith('/message'):  # Handle message send
                    parts = command.split(maxsplit=2)
                    if len(parts) < 3:
                        print("Usage: /message <username> <message>")
                        continue
                    
                    target_user = parts[1]
                    content = parts[2]
                    self.send_message({
                        "type": "message",
                        "target_user": target_user,
                        "content": content
                    })
                elif command.startswith('/help'):
                     print("\nCommands:")
                     print("/chat <username> - Start chat with user")
                     print("/message <username> <message> - Send message to user")
                     print("/quit - Exit the chat")
                else:
                    print("Unknown command. Type /help for commands")
            
            except KeyboardInterrupt:
                break
        
        # Close the socket and exit when the loop ends
        self.socket.close()
        sys.exit(0)
    
    def receive_messages(self):
        """Handle incoming messages from the server and display them to the user."""
        while True:
            try:
                # Receive and decode the server message
                message = json.loads(self.socket.recv(1024).decode())
                
                # Print out the type of message (error, system, or chat)
                if "error" in message:
                    print(f"\nError: {message['error']}")
                elif "system" in message:
                    print(f"\nSystem: {message['system']}")
                elif "from" in message:
                    print(f"\nFrom {message['from']}: {message['content']}")
                    
            except Exception as e:
                print("\nLost connection to server")
                self.socket.close()  # Close the socket if the connection is lost
                sys.exit(1)
    
    def send_message(self, message: dict):
        """Send a message to the server in JSON format."""
        try:
            self.socket.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending message: {str(e)}")

# Run the client when the script is executed
if __name__ == "__main__":  
    client = ChatClient()  # Create a ChatClient instance
    client.start()  # Start the client and connect to the server
