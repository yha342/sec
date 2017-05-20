import socket
import threading

bind_ip =  "0.0.0.0"
bind_port = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind ((bind_ip, bind_port))

server.listen (5)

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

# Das ist der Client handler Thread
def handle_client(client_socket):
    
    # Ausgeben, was der Client sendet
    request = client_socket.recv(1024)
    
    print "[*] Receives: %s" % request
    
    # Ein Paket zurueckschicken
    client_socket.send("ACK!")
    client_socket.close()
    
while True:
    
    client,addr = server.accept()
    
    print "[*] Accespted connection fom %s:%d" % (addr[0],addr[1])

    # Client-Thread anstossen, um eingehende Daten zu verarbeiten
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
