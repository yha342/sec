import sys
import socket
import threading

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((local_host,local_port))
        
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host,local_port)
        print "[!!] Check for other listening socket or correct permissions."
        sys.exit()
        
    print "[*] Listening on %s:%d" % (local_host,local_port)
        
    server.listen(5)
        
    while True:
        client_socket, addr = server.accept()
            
        # Informationen zur lokalen Verbindung ausgeben
        print "[== >] Received incoming connection from %s:%s" % (addr[0],addr[1])
        
        # Thread starten, um mit entferntem Host zu kommunizieren
        proxy_thread = threading.Thread (target=proxy_handler, args=(client_socket,remote_host, remote_port,receive_first))
            
        proxy_thread.start()
		
def proxy_handler(client_socket, remote_host, remote_port, receive_first):

	# Mit entfernten Host verbinden
	remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote_socket.connect((remote_host,remote_port))
	
	# Bei Bedarf Daten vom entfernten Ende empfangen
	if receive_first:
		remote_buffer = receive_from(remote_socket)
		hexdump(remote_buffer)
		
		# An unseren Response-Handler schicken
		remote_buffer = response_handler(remote_buffer)
		
		# Bei BEdarf Daten an unseren lokalen Client senden
		if len(remote_buffer):
			print "[ <==] Sending %d bytes to localhost." %len(remote_buffer)
			client_socket.send(remote_buffer)
	# Nun heisst es in einer Schleife lokal lesen, senden an entfernten Host,
	# waschen, spuelen und wieder von vorne
	while True:
		# Vom lokalen Host lesen
		local_buffer = receive_from(client_socket)
		if len(local_buffer):
		
			print "[== >] Received %d bytes from localhost." % len(local_buffer)
			hexdump(local_buffer)
			
			# An unseren Request-Handler schicken
			local_buffer = request_handler(local_buffer)
			
			# Daten an entfernten Host senden
			remote_socket.send(local_buffer)
			print "[==>] Sent to remote."
			
		# Antwort empfangen
		remote_buffer = receive_from(remote_socket)
		
		if len(remote_buffer):
			print "[ <==] Received %d bytes from remote." % len(remote_buffer)
			hexdump(remote_buffer)
			
			# An unseren Response-Handler schicken
			remote_buffer = response_handler(remote_buffer)
			
			# Antwort an lokalen Socket schicken
			client_socket.send(remote_buffer)
			
			print "[ <==] Sent to localhost."
			
		# Verbindung trennen, wenn an beiden Enden keine Daten mehr vorliegen
		if not len(local_buffer) or not len(remote_buffer):
			client_socket.close()
			remote_socket.close()
			print "[*] No more data, Closing connections."
			
			break
		    
# Schoene Hexdump-Funkion, die direkt aus den hier stehenden Kommentaren uebernommen wurde:
# http://code.activestate.com/recipes/142812-hex-dumper/

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    
    for i in xrange(0, len(src), length):
	s = src[i:i+length]
	hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
	text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
	result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    
    print b'\n'.join(result)
    
def receive_from(connection):
    
    buffer = ""
    
    # Wir setzen das Timeout auf 2 Sekunden, Je nach Ziel muss das angepasst werden
    connection.settimeout(2)
    
    try:
	# In den Puffer einlesen, bis keine weiteren Daten vorhanden sind oder wir unterbrechen
	while True:
	    data = connection.recv(4096)
	    
	    if not data:
		break
	    
	    buffer += data
    except:
	pass
    
    return buffer

# Fuer den entfernten Host gedachte Requests modifizieren

def request_handler(buffer):
    # Paket Aenderungen erfolgen hier
    return buffer

# Fuer den lokalen Host gedachte Requests modifizieren
def response_handler(buffer):
    # Paket Aenderungen erfolgen hier
    return buffer
	
		
            
def main():
    
    # Keine schicken Kommandozeilenoptionen
    
    if len(sys.argv[1:]) != 5:
        print "Usage: ./tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive first]"
        print "Example: ./tcp_proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)
        
    # Lokale Listening-Parmeter festlegen
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    # Entferntes Ziel festlegen
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    # Hier weisen wir unserem Proxy an, die Verbindung herzustellen und
    # Daten zu empfangen, bevor wir an den entfernten Host senden
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
        
    # Nun starten wir unseren Listening-Socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)  
    
main()
        