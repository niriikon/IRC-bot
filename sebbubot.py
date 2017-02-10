#-*- coding:UTF-8 -*-
import socket
import sys
from urllib.request import Request
from urllib.request import urlopen
import configparser
import re

adminlist = ["mirv@otitsun.oulu.fi"]
operatorlist = ["vinvin@otitsun.oulu.fi"]
faggotlist = ["jsloth@otitsun.oulu.fi"]
default_url = ""
time = 0
delay = 24

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")

    parse = config["USERS"]["Adminlist"]
    adminlist = parse.split(',')
    parse = config["USERS"]["Operatorlist"]
    operatorlist = parse.split(',')
    parse = config["USERS"]["Faggotlist"]
    faggotlist = parse.split(',')

    default_url = config["SETTINGS"]["url"]
    time = config["SETTINGS"]["time"]
    delay = config["SETTINGS"]["delay"]

def writeConfig():
    config = configparser.ConfigParser()
    config["USERS"] = {}
    config["USERS"]["Adminlist"] = parseList(adminlist)
    config["USERS"]["Operatorlist"] = parseList(operatorlist)
    config["USERS"]["Faggotlist"] = parseList(faggotlist)

    config["SETTINGS"] = {}
    config["SETTINGS"]["url"] = default_url
    config["SETTINGS"]["time"] = time
    config["SETTINGS"]["delay"] = delay

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

def parseList(list, i=0):
    list_as_string = ""
    while (i < len(list)):
        list_as_string += "{:s},".format(list[i])
        i += 1
    return list_as_string

def joinChannel(socket, channels):
    for i in range(len(channels)):
        channel = channels[i]
        socket.send("JOIN {:s}\n".format(channel).encode('utf-8'))
        print("Joined channel {:s}".format(channel))

    return socket

def getLevel(user):
    if (user in adminlist):
        return 2
    elif (user in operatorlist):
        return 1
    elif (user in faggotlist):
        return -1
    else:
        return 0

def pasteLink(url="http://www.pornhub.com/video/random"):
    req = Request(url)
    res = urlopen(req)
    redirect_url = res.geturl()
    return redirect_url

def runloop(socket):
    while True:
        try:
            response = str(socket.recv(4096),"UTF-8", "replace")
            response = response.split()
            if (len(response) > 3):
                message = parseList(response, 3)
            else:
                message = ""
            print("{}\n".format(response))

            user = response[0].split('!')
            just_nick = user[0]
            if (len(user) >= 2):
                user_level = getLevel(user[1])
            else:
                user_level = 0
            print("just_nick: {:s}".format(user[0]))

            if (user_level >= 2):
                #adminhommat
                #add_operator -CHECK
                #add_admin -CHECK
                #remove_operator -CHECK
                #remove_admin -CHECK
                #config
                if (response[3] == ":!addop"):
                    i = 4
                    while (i < len(response)):
                        operatorlist.append(response[i])
                        i += 1

                elif (response[3] == ":!addadmin"):
                    i = 4
                    while (i < len(response)):
                        adminlist.append(response[i])
                        i += 1

                elif (response[3] == ":!rmop"):
                    if (response[4].isDigit()):
                        operatorlist.pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            operatorlist.pop(response[i])

                elif (response[3] == ":!rmadmin"):
                    if (response[4].isDigit()):
                        adminlist.pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            adminlist.pop(response[i])

                # TODO
                #
                # Vitusti conffeja adminille
                #
                # /TODO
                
            if (user_level >= 1):
                #operaattorihommat
                #set_time
                #set_frequency
                #set_link
                #lotd -CHECK
                if (response[3] == ":!time"):
                    #set_time
                    setTime(response[4])

                elif (response[3] == ":!freq"):
                    #set_frequency
                    setfreq(response[4])

                elif (response[3] == ":!setlink"):
                    #set_link
                    setLink(response[4])

                elif (response[3] == ":!linkplz"):
                    url = pasteLink()
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format("#pornonystavat", url).encode('utf-8'))

            if (user_level == -1):
                #homohommat
                pattern = re.compile("http.://.*|www[.].*|pornhub[.]com.*")
                if (pattern.match(message)):
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format("#pornonystavat", "Ha, gayyyyy!").encode('utf-8'))
            
            pattern = re.compile(".*talo.*")
            print("just_nick == fonillius1: {:b}".format(just_nick == ":fonillius1"))
            print(len(response))
            print("pattern.match(message): {:s}".format(pattern.match(message)))
            if (just_nick == ":fonillius1" and pattern.match(message)):
                socket.send("PRIVMSG {:s} :{:s}\r\n".format("#oty", "yksityistilaisuus").encode('utf-8'))

            #muut hommat
            if ("PING" in response):
                socket.send("PONG {:s}\r\n".format(response[1]).encode('utf-8'))

        except KeyboardInterrupt:
            print("\nGoodbye")
            return None

        except:
           pass


if __name__ == "__main__":
    IPaddress = "irc.oulu.fi"
    portNo = 6667
    nick = "BOTSebbu"
    username = "BOTSebbu"
    realname = "Pornon ystaevae"
    hostname = "IRC"
    servername = "IRCnet"

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((IPaddress, portNo))

    print("Connected to {:s}".format(IPaddress))
    
    clientSocket.send("USER {:s} {:s} {:s} :{:s}\r\n".format(username, hostname, servername, realname).encode('utf-8'))
    clientSocket.send("NICK {:s}\n".format(nick).encode('utf-8'))

    clientSocket = joinChannel(clientSocket, ["#sebbutest", "#pornonystavat", "#oty"])
    #clientSocket = joinChannel(clientSocket, ["#sebbutest"])

    runloop(clientSocket)

else:
    print("pass")
