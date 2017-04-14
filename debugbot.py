#-*- coding:UTF-8 -*-
import socket
import sys
from urllib.request import Request
from urllib.request import urlopen
import configparser
import re
from datetime import datetime, timedelta

adminlist = ["mirv@otitsun.oulu.fi", "vinvin@otitsun.oulu.fi"]
operatorlist = ["glukoosi@glukoosi.com", "piipari@otitsun.oulu.fi", "~kurre@kumikurre.com", "matti@otitsun.oulu.fi"]
faggotlist = ["jsloth@otitsun.oulu.fi", "mirv@otitsun.oulu.fi"]
default_url = ""
time = 0
delay = 24
isFaggot = 0
wappu_tulee = datetime(2017, 4, 20, 18, 0, 0)
wapu_lopu = datetime(2017, 5, 2)

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
    config["USERS"] = {
        "Adminlist": parseList(adminlist),
        "Operatorlist": parseList(operatorlist),
        "Faggotlist": parseList(faggotlist)}

    config["SETTINGS"] = {
        "url": default_url,
        "time": time,
        "delay": delay}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    configfile.close()

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
    if (user in faggotlist):
        fag = 1
    else:
        fag = 0

    if (user in adminlist):
        return 2, fag
    elif (user in operatorlist):
        return 1, fag
    else:
        return 0, fag

def pasteLink(url="http://www.pornhub.com/video/random"):
    req = Request(url)
    res = urlopen(req)
    redirect_url = res.geturl()
    return redirect_url

def getWappu(time_comp=datetime.now()):
    if (wappu_tulee > time_comp):
        #wappuun aikaa
        time_diff = wappu_tulee - time_comp
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        wappu = "Wappuun jäljellä {0}d {1}h {2}m {3}.{4}s!".format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
        return wappu
    else:
        if (wapu_lopu > time_comp):
            # wappua jäljellä
            time_diff = wapu_lopu - time_comp
            hours, remainer = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainer, 60)
            wappu = "Wappua jäljellä {0}d {1}h {2}m {3}.{4}s!".format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
            return wappu
        else:
            return "Wapu ei lopu"

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
            if (len(user) >= 2):
                user_level, isFaggot = getLevel(user[1])
            else:
                user_level = 0
                isFaggot = 0

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
                #writeConfig()

                elif (response[3] == ":!addadmin"):
                    i = 4
                    while (i < len(response)):
                        adminlist.append(response[i])
                        i += 1

                elif (response[3] == ":!addfaggot"):
                    i = 4
                    while (i < len(response)):
                        faggotlist.append(response[i])
                        print("Added {:s} to faggotlist".format(response[i]))
                        i += 1

                elif (response[3] == ":!rmop"):
                    if (response[4].isdigit()):
                        operatorlist.pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            operatorlist.remove(response[i])
                            i += 1

                elif (response[3] == ":!rmadmin"):
                    if (response[4].isdigit()):
                        adminlist.pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            adminlist.remove(response[i])
                            i += 1

                elif (response[3] == ":!rmfaggot"):
                    if (response[4].isdigit()):
                        faggotlist.pop(int(response[4]))
                        print("Removed {:s} from faggotlist".format(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            faggotlist.remove(response[i])
                            print("Removed {:s} from faggotlist".format(response[i]))
                            i += 1

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
                    setTime(response[4])

                elif (response[3] == ":!freq"):
                    setfreq(response[4])

                elif (response[3] == ":!setlink"):
                    setLink(response[4])

                elif (response[3] == ":!linkplz"):
                    if (response[2] == username):
                        url = "Requested by {:s}: {:s}".format(user[0].lstrip(':'), pasteLink())
                    else:
                        url = pasteLink()
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format("#pornonystavat", url).encode('utf-8'))
                    #socket.send("PRIVMSG {:s} :{:s}\r\n".format("#otit.bottest", url).encode('utf-8'))

                elif (response[3] == ":!wappu"):
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format(response[2], getWappu()).encode('utf-8'))

                elif (response[3] == ":!testwappu"):
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format(response[2], getWappu(datetime(2017, 4, 22, 18, 0, 15))).encode('utf-8'))

            if (isFaggot):
                print("homohommat")
                pattern = re.compile("(.*http.://.*)|(.*www[.].*)|(.*pornhub[.]com.*)")
                print(pattern.match(message))
                if (pattern.match(message)):
                    socket.send("PRIVMSG {:s} :{:s}\r\n".format("#pornonystavat", "Ha, gayyyyy!").encode('utf-8'))
                    #socket.send("PRIVMSG {:s} :{:s}\r\n".format("#otit.bottest", "Ha, gayyyyy!").encode('utf-8'))
                    print("Sent messsage to server")
            
            pattern = re.compile(".*talo.*")
            # print("user[0] == fonillius1: {:b}".format(user[0] == ":fonillius1"))
            # print("pattern.match(message): {:s}".format(pattern.match(message)))
            if (user[0] == ":fonillius1" and pattern.match(message)):
                socket.send("PRIVMSG {:s} :{:s}\r\n".format("#oty", "yksityistilaisuus").encode('utf-8'))
                #socket.send("PRIVMSG {:s} :{:s}\r\n".format("#otit.bottest", "yksityistilaisuus").encode('utf-8'))

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

    """

    nick = "TestSebbu"
    username = "TestSebbu"
    realname = "Debuggaamisen ystaevae"
    hostname = "IRC"
    servername = "IRCnet"
    """

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((IPaddress, portNo))

    print("Connected to {:s}".format(IPaddress))
    
    clientSocket.send("USER {:s} {:s} {:s} :{:s}\r\n".format(username, hostname, servername, realname).encode('utf-8'))
    clientSocket.send("NICK {:s}\n".format(nick).encode('utf-8'))

    clientSocket = joinChannel(clientSocket, ["#sebbutest", "#pornonystavat"])
    #clientSocket = joinChannel(clientSocket, ["#sebbutest", "#otit.bottest"])

    try:
        readConfig()
    except:
        pass

    runloop(clientSocket)

else:
    print("pass")
