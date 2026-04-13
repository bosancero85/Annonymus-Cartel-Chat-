import socket
import threading

class ChatServer:
    def __init__(self, host='!!!YOUR IP ADRESS HERE!!!', port=55555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        print(f"Server läuft auf {host}:{port}...")

    def broadcast(self, message, _client):
        """Sendet die verschlüsselte Nachricht an alle außer den Sender."""
        for client in self.clients:
            if client != _client:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            client.close()
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            print(f"{nickname} hat den Server verlassen.")

    def handle(self, client):
        while True:
            try:
                message = client.recv(4096)
                if message:
                    self.broadcast(message, client)
                else:
                    self.remove_client(client)
                    break
            except:
                self.remove_client(client)
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Verbunden mit {str(address)}")
            
            # Der erste Empfang ist der Nickname (unverschlüsselt für Server-Log)
            nickname = client.recv(1024).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.receive()