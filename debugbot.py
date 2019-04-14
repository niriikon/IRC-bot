#-*- coding:UTF-8 -*-
import socket
import sys
from urllib.request import Request
from urllib.request import urlopen
import configparser
import re
from datetime import datetime, timedelta

glVar = {}
glVar['adminlist'] = ['sebu@sebbu.net', '~sebu@sebbu.net']
glVar['operatorlist'] = []
glVar['wapputimes'] = {}
glVar['default_url'] = 'https://c.xkcd.com/random/comic/'
glVar['wappu_tulee'] = datetime(2019, 4, 17, 18, 0, 0)
glVar['wapu_lopu'] = datetime(2019, 5, 2)
glVar['juhannus_tulee'] = datetime(2019, 6, 22, 0, 0, 0)
glVar['BUFFER_LIMIT'] = 475


def readConfig():

    config = configparser.ConfigParser()
    config.read('botconfig.ini')
    
    parse = config.get('USERS', 'Adminlist')
    glVar['adminlist'] = parse.split(',')
    parse = config.get('USERS', 'Operatorlist')
    glVar['operatorlist'] = parse.split(',')

    glVar['default_url'] = config.get('SETTINGS', 'Url')
    glVar['wappulist'] = config.get('SETTINGS', 'Wappu').split(',')
    glVar['wappu_tulee'] = datetime(*map(int, glVar['wappulist']))
    glVar['juhannuslist'] = config.get('SETTINGS', 'Juhannus').split(',')
    glVar['juhannus_tulee'] = datetime(*map(int, glVar['juhannuslist']))

    glVar['wapputimes'] = config._sections['WAPPUTIMES']


def writeConfig():
    config = configparser.ConfigParser()
    config.add_section('USERS')
    config.set('USERS', 'Adminlist', parseList(glVar['adminlist']))
    config.set('USERS', 'Operatorlist', parseList(glVar['operatorlist']))

    config.add_section('SETTINGS')
    config.set('SETTINGS', 'Url', glVar['default_url'])
    config.set('SETTINGS', 'Wappu',
        '{0},{1},{2},{3},{4},{5}'.format(glVar['wappu_tulee'].year, glVar['wappu_tulee'].month, glVar['wappu_tulee'].day, glVar['wappu_tulee'].hour, glVar['wappu_tulee'].minute, glVar['wappu_tulee'].second))
    config.set('SETTINGS', 'Juhannus',
        '{0},{1},{2},{3},{4},{5}'.format(glVar['juhannus_tulee'].year, glVar['juhannus_tulee'].month, glVar['juhannus_tulee'].day, glVar['juhannus_tulee'].hour, glVar['juhannus_tulee'].minute, glVar['juhannus_tulee'].second))

    config.add_section('WAPPUTIMES')
    for key in glVar['wapputimes']:
        config.set('WAPPUTIMES', key, glVar['wapputimes'][key])

    with open('botconfig.ini', 'w') as configfile:
        config.write(configfile)
    configfile.close()

def say(socket, message):
    # Take message (as string.encode('utf-8')) and split payload into 510 byte chunks
    # Send first chunk
    # Send a false command, such as BOTFLOOD
    # Send the next chunk
    # REPEAT
    cmd, channel, body = message.split(maxsplit=2)
    body = body.lstrip(':'.encode('utf-8'))
    header_l = len(cmd) + len(channel) + len('  :'.encode('utf-8'))
    lim = glVar['BUFFER_LIMIT'] - header_l
    print('Header length is: {} and payload chunk size is: {} ({} in total)'.format(header_l, lim, header_l + lim))

    payload = []

    while (len(body) > lim):
        payload.append(body[:lim])
        body = body[lim:]
    payload.append(body[:])

    for msg in payload:
        socket.send(cmd + ' '.encode('utf-8') + channel + ' :'.encode('utf-8') + msg + '\r\n'.encode('utf-8'))
        if (len(msg) >= lim):
            socket.send('FLOODCHECK Writing long message\r\n'.encode('utf-8'))
            response = str(socket.recv(4096),'UTF-8', 'replace')

def parseList(list_in, i=0):
    list_as_string = ''
    while (i < len(list_in)):
        list_as_string += '{:s},'.format(list_in[i])
        i += 1
    return list_as_string.rstrip(',')

def joinChannel(socket, channels):
    """
    for i in range(len(channels)):
        socket.send('JOIN {:s}\n'.format(channels[i]).encode('utf-8'))
        print('Joined channel {:s}'.format(channels[i]))
    """
    socket.send('JOIN {:s}\r\n'.format(channels).encode('utf-8'))
    print('Attempting to join channel(s): {:s}'.format(channels))

def getLevel(user):
    if (user in glVar['adminlist']):
        return 2
    elif (user in glVar['operatorlist']):
        return 1
    else:
        return 0

def pasteLink(url):
    req = Request(url)
    res = urlopen(req)
    return res.geturl()

def getWappu(time_comp=''):
    if (time_comp == ''):
        time_comp = datetime.now()

    if (glVar['wappu_tulee'] > time_comp):
        #wappuun aikaa
        time_diff = glVar['wappu_tulee'] - time_comp
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        return 'Wappuun jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)

    else:
        if (glVar['wapu_lopu'] > time_comp):
            # wappua jäljellä
            time_diff = glVar['wapu_lopu'] - time_comp
            hours, remainer = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainer, 60)
            return 'Wappua jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)

        else:
            return 'Wapu ei lopu'

def getUserWappu(user):
    wappustring = glVar['wapputimes'][user].split(',')
    wappu_begin = datetime(int(wappustring[0]), int(wappustring[1]), int(wappustring[2]), int(wappustring[3]), int(wappustring[4]), int(wappustring[5]))
    time_comp = datetime.now()
    if (wappu_begin < time_comp):
        #wappua mennyt
        time_diff = time_comp - wappu_begin
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        return '{0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)

    else:
        return None

def getJuhannus(time_comp=''):
    if (time_comp == ''):
        time_comp = datetime.now()

    if (glVar['juhannus_tulee'] > time_comp):
        #juhannukseen aikaa
        time_diff = glVar['juhannus_tulee'] - time_comp
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        return 'Juhannukseen jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)


def runloop(socket):

    while True:
        try:
            response = str(socket.recv(4096),'UTF-8', 'replace')
            response = response.split()
            if (len(response) > 3):
                message = parseList(response, 3)
            else:
                message = ''
            if response != []:
                print('Message in:\t{}\n'.format(response))
            else:
                print('Connection refused')
                return None


            user = response[0].split('!')
            # Can username or client server have ! in name?
            if (len(user) >= 2):
                user_level = getLevel(user[1])
            else:
                user_level = 0
                # Mainly for PING messages, also a common fallback


            if (user_level == 2):
                #admin commands:
                #
                #add operator -CHECK
                #add admin -CHECK
                #remove operator -CHECK
                #remove admin -CHECK
                #reload config -CHECK
                #get botinfo

                if (response[3] == ':!addop'):
                    i = 4
                    while (i < len(response)):
                        glVar['operatorlist'].append(response[i])
                        i += 1
                    writeConfig()

                elif (response[3] == ':!addadmin'):
                    i = 4
                    while (i < len(response)):
                        glVar['adminlist'].append(response[i])
                        i += 1
                    writeConfig()

                elif (response[3] == ':!rmop'):
                    if (response[4].isdigit()):
                        glVar['operatorlist'].pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            glVar['operatorlist'].remove(response[i])
                            i += 1
                    writeConfig()

                elif (response[3] == ':!rmadmin'):
                    if (response[4].isdigit()):
                        glVar['adminlist'].pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            glVar['adminlist'].remove(response[i])
                            i += 1
                    writeConfig()

                elif (response[3] == ':!setlink'):
                    glVar['default_url'] = response[4]
                    writeConfig()
                    print('Default url changed: {}'.format(glVar['default_url']))

                elif (response[3] == ':!teekkariwappu'):
                    wappulist = response[4].split(',') # Format: 2017,4,20,18,0,0
                    glVar['wappu_tulee'] = datetime(*map(int, wappulist))
                    writeConfig()

                elif (response[3] == ':!setjussi'):
                    juhannuslist = response[4].split(',')
                    glVar['juhannus_tulee'] = datetime(*map(int, juhannuslist))
                    writeConfig()

                elif (response[3] == ':!reload'):
                    readConfig()


                
            # if (user_level >= 1):
                #operator commands:
                #
                #none atm
                

            #server PING message:
            if ('PING' in response):
                socket.send('PONG {:s}\r\n'.format(response[1]).encode('utf-8'))


            #any_user commands:
            #
            #random link -CHECK
            #wappucounter -CHECK
            #per user -wappucounter -CHECK
            #juhannuscounter -CHECK
            #gibeOps -CHECK
            #tuppi matchmaking
            elif (response[3] == ':!help'):
                # longtext = 'This is just some really long text. This is supposed to be replaced with a help post, explaining how all the commands work. For example, when you type in \'!help\', you will be sent this entire text as query. Currently the command \'!who\' is used only for testing the fetching of user\'s connection information, based on their nick. I was surprised at how difficult it is to write a meaningless post that has to exceed a set length, which in this case 512 bytes. It is important to notice, that it is actually 512 bytes, and not 512 characters. Once the string is properly encoded, it uses either 1 or 2 bytes per character (in practise). This is just some really long text. This is supposed to be replaced with a help post, explaining how all the commands work. For example, when you type in \'!help\', you will be sent this entire text as query. Currently the command \'!who\' is used only for testing the fetching of user\'s connection information, based on their nick. I was surprised at how difficult it is to write a meaningless post that has to exceed a set length, which in this case 512 bytes. It is important to notice, that it is actually 512 bytes, and not 512 characters. Once the string is properly encoded, it uses either 1 or 2 bytes per character (in practise).This is just some really long text. This is supposed to be replaced with a help post, explaining how all the commands work. For example, when you type in \'!help\', you will be sent this entire text as query. Currently the command \'!who\' is used only for testing the fetching of user\'s connection information, based on their nick. I was surprised at how difficult it is to write a meaningless post that has to exceed a set length, which in this case 512 bytes. It is important to notice, that it is actually 512 bytes, and not 512 characters. Once the string is properly encoded, it uses either 1 or 2 bytes per character (in practise).'
                helptext = '!help - Display this message.    ### !linkplz - Request a random link from a site set by bot operators.    ### !wappu - Wappucounter. If user\'s Wappu is set, also displays that.    ### !setwappu - Set the beginning of user\'s Wappu. If no parameters are given, current time is used. Accepted time formats are \"!setwappu d.m.y\" and \"!setwappu d.m.y hh:mm:ss\", for example; \"!setwappu 1.5.2019 12:34:56\"    ### !juhannus - Juhannuscounter'
                say(socket, 'PRIVMSG {:s} :{:s}'.format(user[0].lstrip(':'), helptext).encode('utf-8'))
                helptext = 'Bot flooding may result in a ban. If you have been banned accidentally, please contact a bot operator or admin.'
                say(socket, 'PRIVMSG {:s} :{:s}'.format(user[0].lstrip(':'), helptext).encode('utf-8'))

            elif (response[3] == ':!linkplz'):
                url = pasteLink(glVar['default_url'])
                if (response[2] == username):
                    say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(user[0].lstrip(':'), url).encode('utf-8'))
                else:
                    # socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#sebbutest', url).encode('utf-8'))
                    say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(response[2], url).encode('utf-8'))

            elif (response[3] == ':!wappu'):
                # socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], getWappu()).encode('utf-8'))
                say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(response[2], getWappu()).encode('utf-8'))
                if (user[1] in glVar['wapputimes']):
                    wappuoutput = getUserWappu(user[1])
                    if (wappuoutput != None):
                        wappuoutput = '{:s}:n Wappua on kulunut {:s}'.format(user[0].lstrip(':'), wappuoutput)
                        # socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))
                        say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))
                    else:
                        wappuoutput = '{:s}:n Wappu ei ole vielä alkanut.'.format(user[0].lstrip(':'))
                        # socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))
                        say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))

            elif (response[3] == ':!setwappu'):
                if (len(response) > 4):
                    pattern = re.compile('([0-9]{1,2}[.]){2}[0-9]{4}') # pattern for date d.m.y
                    pattern2 = re.compile('([0-9]{2}:){2}[0-9]{2}') # pattern for time hh:mm:ss
                    print(pattern.match(response[4]))
                    if (len(response) > 5):
                        print(pattern2.match(response[5]))
                        if (pattern2.match(response[5])):
                            wapputime = response[5].split(':')
                            wapputime = [int(wapputime[0]), int(wapputime[1]), int(wapputime[2])]
                        else:
                            wapputime = [0, 0, 0]
                    else:
                        wapputime = [0, 0, 0]

                    if (pattern.match(response[4])):
                        wappudate = response[4].split('.')
                        wappudate = [int(wappudate[0]), int(wappudate[1]), int(wappudate[2])]
                        outputdict = '{:d},{:d},{:d},{:d},{:d},{:d}'.format(wappudate[2], wappudate[1], wappudate[0], wapputime[0], wapputime[1], wapputime[2])
                        glVar['wapputimes'][user[1]] = outputdict
                        outputstring = ':n Wappu alkoi {:d}.{:d}.{:d} {:d}:{:d}:{:d}'.format(wappudate[0], wappudate[1], wappudate[2], wapputime[0], wapputime[1], wapputime[2])
                        # socket.send('PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0].lstrip(':'), outputstring).encode('utf-8'))
                        say(socket, 'PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0].lstrip(':'), outputstring).encode('utf-8'))
                        writeConfig()
                
                else:
                    wappudate = datetime.now()
                    wappuoutput = '{0},{1},{2},{3},{4},{5}'.format(wappudate.year, wappudate.month, wappudate.day, wappudate.hour, wappudate.minute, wappudate.second)
                    glVar['wapputimes'][user[1]] = wappuoutput
                    outputstring = ':n Wappu alkoi {}.{}.{} {}:{}:{}'.format(wappudate.day, wappudate.month, wappudate.year, wappudate.hour, wappudate.minute, wappudate.second)
                    # socket.send('PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0], outputstring).encode('utf-8'))
                    say(socket, 'PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0], outputstring).encode('utf-8'))
                    writeConfig()

            elif (response[3] == ':!juhannus'):
                # socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], getJuhannus()).encode('utf-8'))
                say(socket, 'PRIVMSG {:s} :{:s}\r\n'.format(response[2], getJuhannus()).encode('utf-8'))

            elif (response[3] == ':!ops'):
                print('Giving ops to {:s}'.format(user[0].lstrip(':')).encode('utf-8'))
                socket.send('MODE {:s} +o {:s}\r\n'.format(response[2], user[0].lstrip(':')).encode('utf-8'))

            # Testing username and server fetching with WHOIS
            elif (response[3] == ':!who'):
                socket.send('WHOIS {:s}\r\n'.format(user[0].lstrip(':')).encode('utf-8'))
                response = str(socket.recv(4096),'UTF-8', 'replace')
                response = response.split()
                print('User\'s {:s} connection is: {:s}!{:s}'.format(response[3], response[4], response[5]))

                """
                Define a function 'nickToUser' which takes socket and nickname as parameters and returns
                user@server to be used by admin/operator/etc lists.
                """



        except KeyboardInterrupt:
            socket.send('QUIT :Goodbye\r\n'.encode('utf-8'))
            print('\nGoodbye')
            return None
        
        except:
           pass


if __name__ == '__main__':
    
    IPaddress = 'irc.oulu.fi'
    portNo = 6667


    nick = 'TestSebbu'
    username = 'TestSebbu'
    realname = 'Debuggaamisen ystaevae'
    hostname = 'IRC'
    servername = 'IRCnet'
    

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((IPaddress, portNo))

    print('Connected to {:s}'.format(IPaddress))
    
    clientSocket.send('NICK {:s}\r\n'.format(nick).encode('utf-8'))
    clientSocket.send('USER {:s} {:s} {:s} :{:s}\r\n'.format(username, hostname, servername, realname).encode('utf-8'))

    joinChannel(clientSocket, '#sebbutest')

    """
    readConfig()
    """
    try:
        readConfig()
    except:
        pass
    

    runloop(clientSocket)
    clientSocket.close()
