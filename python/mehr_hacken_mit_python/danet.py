import sys
import socket
import getopt
import threading
import subprocess

# Einige globale variablen definieren
listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0

def usage():
    print "Danis Net Tool"
    print
    print "Usage: danet.py -t target_host -p port"
    print "-l -listen                   - listen on [host]:[port] for incoming connections"
    print "-e -execute=file_to_run      - execute the given file upon receving a connection"
    print "-c -command                  - initalizing a command shell"
    print "-u -upload=destination       - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examplet: "
    print "danet.py -t 192.168.0.1 -p 5555 -l -c"
    print "danet.py -t 192.168.0.1 -p 5555 -l -u='c:\\target.exe'"
    print "danet.py -t 192.168.0.1 -p 5555 -l -e='cat /etc/passwd'"
    print "echo 'ABCDEFGHI' | ./danet.py -t 192.168.11.12 -p 135"
    sys.exit(0) 
    
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Verbindung zum Zielhost
        client.connect((target,port))
        
        if len(buffer):
            client.send(buffer)
            
        while True:
            
            # Auf Daten warten
            recv_len = 1
            response = ""
            
            while recv_len:
                
                data     = client.recv(4096)
                recv_len = len(data)
                response+= data
                
                if recv_len < 4096:
                    break
                
            print response,
            
            # Auf weitere Eingabe warten
            buffer += "\n"
            
            # Daten senden
            client.send(buffer)
            
    except:
        
        print "[*] Exception! Exiting."
        
        # Verbindung sauber schliessen
        client.close()
        
def server_loop():
    global target
    
    # Ist kein Ziel definiert, horchen wir an allen Interfaces
    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        # Thread zur Verarbeitung des neunen Clients starten
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()
        
def run_command(command):
    
    #Newline entfernen
    command = command.rstrip()
    
    # Befehl ausfuehren und Ausgabe zurueckgeben
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
        
    # Ausgabe an den Cient zurueckschicken
    return output
	
def client_handler(client_socket):
	global upload
	global execute
	global command
	
	# Auf Upload pruefen
	if len(upload_destination):
		
		# Alle Bytes einlesen und ans ZIel schreiben
		file_buffer = ""
		
		# Daten einlesen, bis keine mehr vorhanden sind
		while True:
			data = client_socket.recv(1024)
			
			if not data:
				break
			else:
				file_buffer += data
				
		# Nun versuchen wir, diese Daten zu schreiben
		
		try:
			file_descriptor = open(upload_destination,"wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()
			
			# und den Erfolg bestaetigen
			client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
			
		except:
			client_socket.send("Failed to save file to %s\r\n" % upload_destination)
			
	#Auf Befehlsausfuehrung pruefen
	if len(execute):
		
		# Den Befehl ausfuehren
		output = run_command(execute)
		
		client_socket.send(output)
	
	# Zusaetzliche Schleife, wenn eine Shell angefordert wurde
	if command:
	
		while True:
			# Einen einfachen Prompt ausgeben
			client_socket.send(" <DANET:# > ")
			
				# Empfangen bis zum Linefeed (enter key)
			cmd_buffer = ""
			while "\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024)
				
			# Befehlsausgabe abfangen
			response = run_command(cmd_buffer)
			
			# Antowrt zueruecksenden
			client_socket.send(response)

    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    # Kommandizeilenoption verarbeiten
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","comman","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
    for o,a in opts:
        if o in ("-h","-help"):
            usage()
        elif o in ("-l","-listen"):
            listen = True
        elif o in ("-e","-execute"):
            execute = a
        elif o in ("-c","-commandshell"):
            command = True
        elif o in ("-u","-upload"):
            upload_destination = a
        elif o in ("-t","-target"):
            target = a
        elif o in ("-p", "-port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
            
    # Horchen wir oder senden wir nut Daten von stdin?
    if not listen and len(target) and port > 0:
        
        # Den Puffer ueber die Kommandozeile einzulesen blockiert,
        # d.h., wir muessen Ctrl-D senden, wenn wir keine Eingabe
        # ueber stdin erfolgt.
        buffer = sys.stdin.read()
        
        # Daten senden
        client_sender(buffer)
        
    # Wir horchen und laden moeglicherweise Dinge hoch,
    # fuehren Befehle aus oder starten eine Shell. Das haengt
    # von der obigen Kommandozeilenoption ab.
    if listen:
        server_loop()


main()


    
