#!/usr/bin/python3

###########################################
##Mutli Client-Server Chat Application	 ##
##Author: Devpriya Nalin				 ##
##Started: 31 July, 2018				 ##
##Base Finished: August 4, 2018			 ##
##Finished: Still in Progress			 ##
###########################################

#FEATURE THOUGHT#
#Encrypt a file and send it through the internet

#BUG#
#No known bugs as of know

import socket
import _thread
import time
import subprocess
import os

client_conn = {}
client_info = {} #stores the information related to the clients who are connected to the server
clients_waiting = [] #stores the names of all the clients who are waiting for connections

#####################################################################################
#THIS FUNCTION HANDLES RECEIVING messages############################################
#####################################################################################
def sendMessage(client2Socket, clientSocket,clientName,client2Name):
	#receive messages from the previous client and send it to the  client
	while True:
		mesg = client2Socket.recv(1024)
		print("{} receiving: {}".format(clientName,mesg.decode('utf-8')))
		if mesg.decode('utf-8')!='#QUIT#':
			try:
				clientSocket.sendall(mesg)
			except:
				exit()
		else:
			print("{} has quit".format(client2Name))
			clientSocket.sendall(mesg)
			client2Socket.close()
			clientSocket.close()
			exit()





########################################################################################
####THIS FUNCTION HANDLES THE INITIATING CLIENT#########################################
########################################################################################
def clientIni(clientSocket,client_name):

	######################
	#Client 1            #
	#initiates connection#
	######################

	import socket

	global client_conn

	while True:
		#receiving the client's name that client1 want's to connect to
		client2 =  clientSocket.recv(1024).decode('utf-8')
			
		if (client2 in client_info) and (client2 == client_name):
			clientSocket.sendall("Trse".encode('utf-8'))
			continue

		elif client2 in client_info:

			#Test part delete if breaks
			client_conn[client2] = client_name
			################################

			clientSocket.sendall("True".encode('utf-8'))
			client2Socket = socket.socket()
			client2Socket.connect(('127.0.0.1',2090))
			#sending the name of the client
			client2Socket.sendall(client_name.encode('utf-8'))

			#sending a confirmation message to the client
			clientSocket.sendall(("Connected to {}".format(client2)).encode('utf-8'))
			#starting thread for receiving and sending messages
			_thread.start_new_thread(sendMessage,(client2Socket, clientSocket,client_name,client2))
			while True:
				mesg = clientSocket.recv(1024)
				if mesg.decode('utf-8')!='q':
					try:
						client2Socket.sendall(mesg)
					except:
						client2Socket.close()
						clientSocket.close()
						exit()
				else:
					client2Socket.sendall('#QUIT#'.encode('utf-8'))
					client2Socket.close()
					clientSocket.close()
					break
			exit()
			
		else:
			clientSocket.sendall("False".encode('utf-8'))
			continue



#########################################################################################
####THIS FUNCTION HANDLES THE WAITING CLIENT#############################################
#########################################################################################
def clientWait(clientSocket,client_name):

	######################
	#Client 1 waits for  #
	#connection          #
	######################


	import socket

	global sessionSocket
	global clients_waiting
	global client_conn

	client_conn[client_name] = " "

	#putting the name of the client who is waiting in the clients_waiting list
	clients_waiting.append(client_name)

	#Only start accepting connections if the connection is requested by the user
	while True:
		if client_conn[client_name] == " ":#Check if the initiating client wants to connect to this particular client_name
			continue
		else:#If yes then break out
			break

	while True:
		client2Socket,sessAddr = sessionSocket.accept()

		try:
			del client_conn[client_name]
		except:
			print("Key error! Shit!")

		client2_name = client2Socket.recv(1024).decode('utf-8')#what?!
		print(client_name," established connection with ",client2_name)##debug line##
		print("####{} connected to {} at {}####".format(client_name,client2_name,sessAddr[1]))
	
		clientSocket.sendall(("Connected to {}".format(client2_name)).encode('utf-8'))
		print("Confirmation message sent to", client_name)

		_thread.start_new_thread(sendMessage,(client2Socket, clientSocket,client_name,client2_name))
		while True:
			mesg = clientSocket.recv(1024)
			if mesg.decode('utf-8')!='q':
				try:
					client2Socket.sendall(mesg)
				except:
					clients_waiting.remove(client_name)
					client2Socket.close()
					clientSocket.close()
					exit()
			
			elif mesg.decode('utf-8')=="#2002?!#":
				clients_waiting.clear()
				client2Socket.sendall('#QUIT#'.encode("utf-8"))
				client2Socket.close()
				clientSocket.close()
				exit()

			else:
				client2Socket.sendall('#QUIT#'.encode('utf-8'))
				client2Socket.close()
				clientSocket.close()
				clients_waiting.remove(client_name)
				exit()



##########################################################################################
#THIS FUNCTION HANDLES THE CLIENT CONNECTION TO THE SERVER################################
##########################################################################################
def client_connection(clientSocket,addr):

	#######################################
	##The function handles the connection##
	##and takes the username along with  ##
	##the connection type and then calls ##
	##the appropriate function based on  ##
	##the connection type                ##
	#######################################

	import socket
	
	#asking the client for a name and storing it in the dictionary
	client_name = clientSocket.recv(1024).decode('utf-8')
	client_info[client_name] = addr
	print("####Got the name and stored it in my database#####")
	print(client_info)
	print("")

	#receiving the connection type from the client
	connType = clientSocket.recv(1024).decode('utf-8')
	
	if 'initiate' in connType:
		_thread.start_new_thread(clientIni,(clientSocket,client_name))

	elif 'wait' in connType:
		_thread.start_new_thread(clientWait,(clientSocket,client_name))
	exit()				



##############################################
#BROADCASTING THE NAME OF THE WAITING CLIENTS#
##############################################
def broadcastMessage(connection,test):
	global clients_waiting
	global clientWaitstatus

	waitingData = ""
	dataSent = ""
	iteration = 0

	while True:
		if clients_waiting:#Check if any client is waiting or not
			waitingData = ";".join(clients_waiting)
		else:
			continue

		if iteration>0:#If the code has already run and stored a name in the list
			if not waitingData == dataSent:
				connection.sendall(waitingData.encode('utf-8'))
			else:
				try:
					connection.sendall("same".encode('utf-8'))
				except:
					print("Client Ended the connection")
					connection.close()
					exit()

			dataSent = waitingData

			confirm = connection.recv(1024).decode('utf-8')
			if confirm == "yes":
				pass
			elif confirm == "no":
				connection.close()
				exit()
		else:
			connection.sendall(waitingData.encode('utf-8'))
			dataSent = waitingData
			confirm = connection.recv(1024).decode('utf-8')
			if confirm == "yes":
				pass

		#Increment iteration 
		iteration = iteration + 1

def broadcast():
	import socket

	while True:
		connection, addr = broadcastSocket.accept()
		print("Connected to a client who wants to initiate connection at {} on {}".format(addr[0],addr[1]))
		_thread.start_new_thread(broadcastMessage,(connection,"lol"))


########################################################################################
#STARTING POINT OF SERVER###############################################################
########################################################################################

#Checking if the port is busy or not
iteration = 0
pid = 0

checkPort = "lsof -i :2090"
commList = checkPort.split(" ")
try:
	output = subprocess.check_output(commList).decode('utf-8')
	cleanOutput = output.split(" ")

	for i in cleanOutput[::-1]:
		if not i == "":
			if i == "nalin":
				iteration = iteration + 1
				continue
			if iteration == 1:
				pid  = int(i)
				break

#Killing the pid if port was active 
except:
	if not pid == 0:
		print("Killing pid ",pid)
		os.system("sudo kill {}".format(pid))


#Port for server's connection between clients
sessionSocket = socket.socket()
try:
	sessionSocket.bind(('',2090))
	print("Binded to port 2090 for client session connection")
except:
	print("The port for in-server client connections is in use, try again after some time.")
	exit()
sessionSocket.listen(3)


#Port for server-client connections
clientConn = socket.socket()
try:
	clientConn.bind(('',3090))
	print("Binded to port 3090 for client-server connections")
except:
	print("The port for client-server connections is in use, try after some time.")
	exit()
clientConn.listen(3)


broadcastSocket = socket.socket()#For broadcasting the names of the waiting clients
broadcastSocket.bind(('',1090))
print("Binded to port 1090 for broadcasting")
print("")
broadcastSocket.listen(1)



try:#Catching the keyboard exception

	#The main loop for connecting to clients
	while True:
		s, addr = clientConn.accept()

		print("##Connected to {} at {}##".format(addr[0],addr[1]))

		_thread.start_new_thread(client_connection,(s,addr))

		print("Client connection thread started")

		_thread.start_new_thread(broadcast,())
		print("Broadcast thread started")
		print("")

except:
	print("Exiting the server!")