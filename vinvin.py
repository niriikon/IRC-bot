#-*- coding:UTF-8 -*-
import socket
from urllib.request import Request
from urllib.request import urlopen

def joinChannel(socket, channels):
	for i in range(len(channels)):
		channel = channels[i]
		socket.send("JOIN {:s}\n".format(channel).encode('utf-8'))
		print("Joined channel {:s}".format(channel))

	return socket

def pasteLink(url="http://www.pornhub.com/video/random"):
	req = Request(url)
	res = urlopen(req)
	redirect_url = res.geturl()
	print(redirect_url)
	return redirect_url

def runloop(socket):
	while True:
		response = str(socket.recv(4096),"UTF-8", "replace")
		response = response.split()
		print("{}\n".format(response))

		print(response[1])
		if ("PING" in response):
			socket.send("PONG {:s}\r\n".format(response[1]).encode('utf-8'))
		elif (":lotd" in response):
			sender = response[0].split("!")
			print(sender)
			if (sender[1] == "mirv@otitsun.oulu.fi" or sender[1] == "vinvin@otitsun.oulu.fi"):
				url = pasteLink()
				socket.send("PRIVMSG {:s} :{:s}\r\n".format("#sebbutest", url).encode('utf-8'))


if __name__ == "__main__":
	IPaddress = "irc.oulu.fi"
	portNo = 6667
	nick = "BOTSebbu"
	username = "BOTSebbu"
	realname = "Pornon Ystaevae"
	hostname = "IRC"
	servername = "IRCnet"

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.connect((IPaddress, portNo))
	#response = clientSocket.recv(4096)
	#print("{:s}\n".format(response))
	print("Connected to {:s}".format(IPaddress))
	
	clientSocket.send("USER {:s} {:s} {:s} :{:s}\r\n".format(username, hostname, servername, realname).encode('utf-8'))
	print("Set USER to {:s}".format(username))
	clientSocket.send("NICK {:s}\n".format(nick).encode('utf-8'))
	print("Set NICK to {:s}".format(nick))
	clientSocket = joinChannel(clientSocket, ["#sebbutest", "#pornonystavat"])
	#clientSocket.send("PRIVMSG {:s} : {:s}\r\n".format("#sebbutest", "asdf").encode('utf-8'))
	
	#response = clientSocket.recv(4096)
	#print("{:s}\n".format(response))
	print("Wrote asdf to #sebbutest")

	runloop(clientSocket)

else:
	print("pass")
