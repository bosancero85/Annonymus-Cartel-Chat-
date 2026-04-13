import socket
import threading
import customtkinter as ctk
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# --- KRYPTO LOGIK ---
# In einer echten E2EE App würde dieser Key per RSA ausgetauscht werden.
# Hier nutzen wir einen statischen Key für den Demo-Kanal.
SHARED_KEY = b'12345678901234567890123456789012' # 32 Bytes = AES-256

def encrypt_msg(message):
    aesgcm = AESGCM(SHARED_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
    return nonce + ciphertext

def decrypt_msg(data):
    try:
        aesgcm = AESGCM(SHARED_KEY)
        nonce = data[:12]
        ciphertext = data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
    except:
        return "[Fehler beim Entschlüsseln]"

# --- UI LOGIK ---
class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure mIRC Clone")
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")

        # Netzwerk Setup
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = f"User_{os.urandom(2).hex()}"
        
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Seitenleiste
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.logo = ctk.CTkLabel(self.sidebar, text="SECURE CHAT", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.pack(pady=20)
        
        # Chat Bereich
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.text_area = ctk.CTkTextbox(self.chat_frame, state="disabled", wrap="word")
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.msg_entry = ctk.CTkEntry(self.chat_frame, placeholder_text="Sichere Nachricht senden...")
        self.msg_entry.pack(fill="x", padx=5, pady=5)
        self.msg_entry.bind("<Return>", self.send_message)

        # Verbindung starten
        try:
            self.client.connect(('!!!YOUR IP ADRESS HERE!!!', 55555))
            self.client.send(self.nickname.encode('utf-8'))
            
            thread = threading.Thread(target=self.receive)
            thread.daemon = True
            thread.start()
        except:
            self.display_message("System", "Verbindung zum Server fehlgeschlagen!")

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            timestamp = datetime.now().strftime("%H:%M")
            full_msg = f"[{timestamp}] {self.nickname}: {msg}"
            
            # UI lokal aktualisieren
            self.display_message("Ich", msg)
            
            # Verschlüsseln und Senden
            encrypted = encrypt_msg(full_msg)
            self.client.send(encrypted)
            self.msg_entry.delete(0, 'end')

    def receive(self):
        while True:
            try:
                data = self.client.recv(4096)
                if data:
                    decrypted = decrypt_msg(data)
                    self.display_message("Partner", decrypted, is_remote=True)
            except:
                break

    def display_message(self, sender, msg, is_remote=False):
        self.text_area.configure(state="normal")
        time = datetime.now().strftime("%H:%M")
        prefix = f"[{time}] {sender}: " if not is_remote else ""
        self.text_area.insert("end", f"{prefix}{msg}\n")
        self.text_area.configure(state="disabled")
        self.text_area.see("end")

if __name__ == "__main__":
    app = ChatClient()
    app.mainloop()