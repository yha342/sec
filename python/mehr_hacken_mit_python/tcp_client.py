import socket

target_host = "localhost"
target_port = 9999

# Socket-Objekt erzeugen
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Clientverbindung herstellen
client.connect((target_host,target_port))

# Einige Daten senden
client.send("GET / HTTP/1.1\r\nHost: google.ch\r\n\r\n")

# Einige Daten empfangen
response = client.recv(4096)

print response
