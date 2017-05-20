import socket

target_host = "127.0.0.1"
target_port = 80

# Socket-Objekt erzeugen
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Einige Daten senden
client.sendto("AAABBBCCC", (target_host, target_port))

# Einige Daten empfangen
data,addr = client.recvfrom(4096)

print data
