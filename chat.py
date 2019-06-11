#!/usr/bin/python3

###########################################
##Mutli Client-Server Chat Application	 ##
##Author: Devpriya Nalin				 ##
##Started: 31 July, 2018				 ##
##Base Finished: August 4, 2018			 ##
##Finished: Still in Progress			 ##
###########################################

import socket
import _thread
import tkinter
import random
import time

def displayBroadcast(socket,test):
	childWindow = tkinter.Tk(className=" Clients Waiting")
	childWindow.configure(bg='lightblue')
	childWindow.geometry("260x260")

	#The window where you can see all the people who are waiting
	scrollbar = tkinter.Scrollbar(childWindow, orient="vertical")
	lbchild = tkinter.Listbox(childWindow,font='2', width=40, height=10, yscrollcommand=scrollbar.set)
	lbchild.pack(side="top",fill="both",expand=True)

	exitButton = tkinter.Button(childWindow,text="Exit",command=childWindow.destroy,fg='red',bd='3',activebackground='red',relief='raised',width=4)
	exitButton.pack(side='bottom')

	_thread.start_new_thread(recvBroadcast,(socket,test,lbchild))

	childWindow.mainloop()



def recvBroadcast(socket,test,lbchild):

	tempStorage = []

	while True:
		broadcast = socket.recv(1024).decode('utf-8')

		if broadcast == "same":
			socket.sendall("yes".encode('utf-8'))
		else:
			data = broadcast.split(';')
			for client in data:
				if not client in tempStorage:
					lbchild.insert("end",client)
					lbchild.see("end")
					lbchild.itemconfig("end", {'fg': 'red'})
					tempStorage.append(client)
				else:
					pass
			socket.sendall("yes".encode('utf-8'))


def getMesg(entry):
	mesg = entry.get()
	entry.delete(0,"end")
	return mesg


def chatDisp(message,option,lb,client2Name):
	if option == 's':
		lb.insert("end","{}: {}".format("Me",message))
		lb.itemconfig("end", {'fg': 'red'})
		lb.see("end")
	elif option == 'r':
		if len(message)>30:
			finalMessage = ""
			spaceSplit = message.split(" ")
			check = 0
			counter = 0
			for item in spaceSplit:
				if check > 30:
					if counter == 1:
						lb.insert("end","{}{}".format(" "*len(client2Name),finalMessage))
						lb.itemconfig("end", {'fg': 'purple3'})
						lb.see("end")
						finalMessage = ""
						check = 0
					else:
						lb.insert("end","{}: {}".format(client2Name,finalMessage))
						lb.itemconfig("end", {'fg': 'purple3'})
						lb.see("end")
						finalMessage = ""
						check = 0
						counter = 1

				check = check + len(item+" ")
				finalMessage = finalMessage + item+ " "
			spaceSplit.clear()
		else:
			lb.insert("end","{}: {}".format(client2Name,message))
			lb.itemconfig("end", {'fg': 'purple3'})
			lb.see("end")


def sendMesg(socket,lb,entry,client2Name):
	mesg = getMesg(entry)
	if mesg!='q':
		#encrypting the message
		encrStr = []
		for letter in mesg:
			encrStr.append(str(ord(letter)))
			encrStr.append(str(chr(random.randint(27,47))))

		socket.sendall((''.join(encrStr)).encode('utf-8'))

		chatDisp(mesg,'s',lb,client2Name)
	else:
		socket.sendall(mesg.encode('utf-8'))
		chatDisp(mesg,'s',lb,client2Name)
		endProgram(socket)			

def listenMesg(socket,lb,client2Name,broadcastSocket):
	while True:
		mesg = socket.recv(1024).decode('utf-8')
		if mesg!="#QUIT#":
			if mesg:
				###decrypting the message###
				asciival = ""
				hdemessage = []
				fdmessage = []

				#removing the ASCII values from the encrypted string soup of characters
				for character in mesg:
					if not (ord(character) in range(27,48)):
						asciival = asciival + character
					else:
						if asciival:
							hdemessage.append(int(asciival))
							asciival = ""

				#converting those ASCII values to their character equivalents
				for asciival in hdemessage:
					fdmessage.append(chr(asciival))

				#converting that list to a string for representation
				message = ''.join(fdmessage)
				chatDisp(message,'r',lb,client2Name)
			else:
				break
		else:
			chatDisp(mesg,'r',lb,client2Name)
			time.sleep(1)
			_thread.interrupt_main()
			break


def endProgram(socket):
	socket.close()
	exit()


def displayMessage(socket,username,userStatus,broadcastSocket):

	#The main interface
	mainWindow = tkinter.Tk(className=" Messages Receieved")
	mainWindow.configure(bg='lightblue')
	mainWindow.title(username)
	mainWindow.geometry("440x470")

	connmesg = socket.recv(1024).decode('utf-8')
	client2Name = connmesg.split(' ')[2]

	connMessage = tkinter.Label(mainWindow,text=connmesg,relief='flat',width=90,height=1,fg='green')
	connMessage.pack()

	scrollbar = tkinter.Scrollbar(mainWindow, orient="vertical")
	scrollbar2 = tkinter.Scrollbar(mainWindow, orient="horizontal")

	entry = tkinter.Entry(mainWindow,bg='white',cursor='arrow',fg='blue',relief='ridge',width='45')
	entry.focus()
	bottomFrame = tkinter.Frame(mainWindow)
	bottomFrame.pack(side='bottom')

	lb = tkinter.Listbox(mainWindow,font='1', width=50, height=20, yscrollcommand=scrollbar.set,xscrollcommand=scrollbar2.set)

	scrollbar.config(command=lb.yview)
	scrollbar2.config(command=lb.xview)

	entry.bind('<Return>',(lambda x: sendMesg(socket,lb,entry,client2Name)))
	entry.pack(side='bottom',pady='10',fill='y',expand=True,ipady='3')

	scrollbar.pack(side="right", fill="y")
	scrollbar2.pack(side='bottom', fill='x')

	lb.pack(side="left",fill="both", expand=True)

	lb.insert("end","****Send q to quit****")
	lb.insert("end","****Welcome to this little Chat Application!****")
	lb.insert("end","****This connection is encrypted****")
	lb.insert("end"," ")
	

	_thread.start_new_thread(listenMesg,(socket,lb,client2Name,broadcastSocket))

	mainWindow.mainloop()
	socket.close()

try: #To catch the keyboard error

	serverConn = socket.socket()

	try:
		#serverConn.connect(('privateserver243.ddns.net',9090))
		serverConn.connect(('',3090))
	except:
		print("###SERVER IS NOT OPERATIONAL###")
		print("###COME BACK LATER###")
		exit()

	#sending the username to the server
	name = input("Username: ")
	serverConn.sendall(name.encode('utf-8'))
	print()

	#asking the user if he wants to wait for a connection or initiate one
	while True:
		connType = input("Initiate or wait?: ")

		if "initiate" in connType:
			serverConn.sendall("initiate".encode('utf-8'))

			while True:
				broadcast = socket.socket()#creating a socket object for receiving broadcasts
				broadcast.connect(('',1090))
				#broadcast.connect(('privateserver243.ddns.net',1090))
				displayBroadcast(broadcast,"sakeofit")
				client2_name = input("User2: ")
				if client2_name:
					serverConn.sendall(client2_name.encode('utf-8'))
					userStatus = serverConn.recv(1024).decode('utf-8')

					if userStatus == 'True':
						displayMessage(serverConn,name,"initiate",broadcast)
					elif userStatus == 'False':
						print("#SERVER: User not found#")
					elif userStatus == 'Trse':
						print("#SERVER: You can't talk to yourself#")
				else:
					print("Username required!")
					continue
				
			
		elif "wait" in connType:
			serverConn.sendall("wait".encode('utf-8'))
			displayMessage(serverConn,name,"wait",serverConn)

		else:
			pass

except:
	print("#########Have a nice day!#########")
	serverConn.close()

