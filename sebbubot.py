#-*- coding:UTF-8 -*-
import socket
import sys
from urllib.request import Request
from urllib.request import urlopen
import configparser
import re
from datetime import datetime, timedelta

glVal = {}
glVal['adminlist'] = ['sebu@sebbu.net', '~sebu@sebbu.net']
glVal['operatorlist'] = ['vinvin@otitsun.oulu.fi']
glVal['faggotlist'] = ['jsloth@otitsun.oulu.fi']
glVal['wapputimes'] = {}
glVal['default_url'] = ''
glVal['delay'] = 24
glVal['wappu_tulee'] = datetime(2017, 5, 1, 0, 0, 0)
glVal['wapu_lopu'] = datetime(2017, 5, 2)
glVal['juhannus_tulee'] = datetime(2017, 6, 23, 18, 0, 0)
glVal['request_buffer'] = []

def readConfig():

    config = configparser.ConfigParser()
    config.read('botconfig.ini')
    
    parse = config.get('USERS', 'Adminlist')
    glVal['adminlist'] = parse.split(',')
    parse = config.get('USERS', 'Operatorlist')
    glVal['operatorlist'] = parse.split(',')
    parse = config.get('USERS', 'Faggotlist')
    glVal['faggotlist'] = parse.split(',')

    glVal['default_url'] = config.get('SETTINGS', 'Url')
    glVal['delay'] = int(config.get('SETTINGS', 'Delay'))
    glVal['wappulist'] = config.get('SETTINGS', 'Wappu').split(',')
    glVal['wappu_tulee'] = datetime(*map(int, glVal['wappulist']))
    glVal['juhannuslist'] = config.get('SETTINGS', 'Juhannus').split(',')
    glVal['juhannus_tulee'] = datetime(*map(int, glVal['juhannuslist']))

    glVal['wapputimes'] = config._sections['WAPPUTIMES']

def writeConfig():
    config = configparser.ConfigParser()
    config.add_section('USERS')
    config.set('USERS', 'Adminlist', parseList(glVal['adminlist']))
    config.set('USERS', 'Operatorlist', parseList(glVal['operatorlist']))
    config.set('USERS', 'Faggotlist', parseList(glVal['faggotlist']))

    config.add_section('SETTINGS')
    config.set('SETTINGS', 'Url', glVal['default_url'])
    config.set('SETTINGS', 'Delay', str(glVal['delay']))
    config.set('SETTINGS', 'Wappu',
        '{0},{1},{2},{3},{4},{5}'.format(glVal['wappu_tulee'].year, glVal['wappu_tulee'].month, glVal['wappu_tulee'].day, glVal['wappu_tulee'].hour, glVal['wappu_tulee'].minute, glVal['wappu_tulee'].second))
    config.set('SETTINGS', 'Juhannus',
        '{0},{1},{2},{3},{4},{5}'.format(glVal['juhannus_tulee'].year, glVal['juhannus_tulee'].month, glVal['juhannus_tulee'].day, glVal['juhannus_tulee'].hour, glVal['juhannus_tulee'].minute, glVal['juhannus_tulee'].second))

    config.add_section('WAPPUTIMES')
    for key in glVal['wapputimes']:
        config.set('WAPPUTIMES', key, glVal['wapputimes'][key])

    with open('botconfig.ini', 'w') as configfile:
        config.write(configfile)
    configfile.close()

def parseList(list_in, i=0):
    list_as_string = ''
    while (i < len(list_in)):
        list_as_string += '{:s},'.format(list_in[i])
        i += 1
    return list_as_string.rstrip(',')

def joinChannel(socket, channels):
    for i in range(len(channels)):
        channel = channels[i]
        socket.send('JOIN {:s}\n'.format(channel).encode('utf-8'))
        print('Joined channel {:s}'.format(channel))

    return socket

def getLevel(user):
    if (user in glVal['faggotlist']):
        fag = 1
    else:
        fag = 0

    if (user in glVal['adminlist']):
        return 2, fag
    elif (user in glVal['operatorlist']):
        return 1, fag
    else:
        return 0, fag

def pasteLink(url='http://www.pornhub.com/video/random'):
    req = Request(url)
    res = urlopen(req)
    redirect_url = res.geturl()
    return redirect_url

def getWappu(time_comp=''):
    if (time_comp == ''):
        time_comp = datetime.now()
    if (glVal['wappu_tulee'] > time_comp):
        #wappuun aikaa
        time_diff = glVal['wappu_tulee'] - time_comp
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        wappu = 'Wappuun jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
        return wappu
    else:
        if (glVal['wapu_lopu'] > time_comp):
            # wappua jäljellä
            time_diff = glVal['wapu_lopu'] - time_comp
            hours, remainer = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainer, 60)
            wappu = 'Wappua jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
            return wappu
        else:
            return 'Wapu ei lopu'

def getUserWappu(user):
    wappustring = glVal['wapputimes'][user].split(',')
    wappu_begin = datetime(int(wappustring[0]), int(wappustring[1]), int(wappustring[2]), int(wappustring[3]), int(wappustring[4]), int(wappustring[5]))
    time_comp = datetime.now()
    if (wappu_begin < time_comp):
        #wappua mennyt
        time_diff = time_comp - wappu_begin
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        wappu = '{0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
        return wappu
    else:
        return None

def getJuhannus(time_comp=''):
    if (time_comp == ''):
        time_comp = datetime.now()
    if (glVal['juhannus_tulee'] > time_comp):
        #jussiin aikaa
        time_diff = glVal['juhannus_tulee'] - time_comp
        hours, remainer = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainer, 60)
        juhannus = 'Juhannukseen jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
        return juhannus
    '''
    else:
        if (juhannus_lopu > time_comp):
            # wappua jäljellä
            time_diff = wapu_lopu - time_comp
            hours, remainer = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainer, 60)
            wappu = 'Wappua jäljellä {0}d {1}h {2}m {3}.{4}s!'.format(time_diff.days, hours, minutes, seconds, time_diff.microseconds)
            return wappu
        else:
            return 'Wapu ei lopu'
    '''

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
                print('{}\n'.format(response))
            else:
                print('Connection refused')
                return None


            user = response[0].split('!')
            if (len(user) >= 2):
                user_level, isFaggot = getLevel(user[1])
            else:
                user_level = 0
                isFaggot = 0

            print('just_nick: {:s}'.format(user[0]))

            if (user_level >= 2):
                #adminhommat
                #add_operator -CHECK
                #add_admin -CHECK
                #remove_operator -CHECK
                #remove_admin -CHECK
                #config
                if (response[3] == ':!addop'):
                    i = 4
                    while (i < len(response)):
                        glVal['operatorlist'].append(response[i])
                        i += 1
                    writeConfig()

                elif (response[3] == ':!addadmin'):
                    i = 4
                    while (i < len(response)):
                        glVal['adminlist'].append(response[i])
                        i += 1
                    writeConfig()

                elif (response[3] == ':!addfaggot'):
                    i = 4
                    while (i < len(response)):
                        glVal['faggotlist'].append(response[i])
                        print('Added {:s} to faggotlist'.format(response[i]))
                        i += 1
                    writeConfig()

                elif (response[3] == ':!rmop'):
                    if (response[4].isdigit()):
                        glVal['operatorlist'].pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            glVal['operatorlist'].remove(response[i])
                            i += 1
                    writeConfig()

                elif (response[3] == ':!rmadmin'):
                    if (response[4].isdigit()):
                        glVal['adminlist'].pop(int(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            glVal['adminlist'].remove(response[i])
                            i += 1
                    writeConfig()

                elif (response[3] == ':!rmfaggot'):
                    if (response[4].isdigit()):
                        glVal['faggotlist'].pop(int(response[4]))
                        print('Removed {:s} from faggotlist'.format(response[4]))
                    else:
                        i = 4
                        while (i < len(response)):
                            glVal['faggotlist'].remove(response[i])
                            print('Removed {:s} from faggotlist'.format(response[i]))
                            i += 1
                    writeConfig()

                elif (response[3] == ':!setlink'):
                    glVal['default_url'] = response[4]
                    writeConfig()
                    print(glVal['default_url'])

                elif (response[3] == ':!teekkariwappu'):
                    wappulist = response[4].split(',') #2017,4,20,18,0,0
                    glVal['wappu_tulee'] = datetime(*map(int, wappulist))
                    writeConfig()

                elif (response[3] == ':!setjussi'):
                    juhannuslist = response[4].split(',')
                    glVal['juhannus_tulee'] = datetime(*map(int, juhannuslist))
                    writeConfig()

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

                if (response[3] == ':!delay'):
                    glVal['delay'] = response[4]
                    writeConfig()

                elif (response[3] == ':!linkplz'):
                    if (response[2] == username):
                        url = 'Requested by {:s}: {:s}'.format(user[0].lstrip(':'), pasteLink(glVal['default_url']))
                    else:
                        url = pasteLink(glVal['default_url'])
                    socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#pornonystavat', url).encode('utf-8'))
                    #socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#sebbutest', url).encode('utf-8'))

            #muut hommat
            if ('PING' in response):
                socket.send('PONG {:s}\r\n'.format(response[1]).encode('utf-8'))

            elif (response[3] == ':!wappu'):
                socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], getWappu()).encode('utf-8'))
                if (user[1] in glVal['wapputimes']):
                    wappuoutput = getUserWappu(user[1])
                    if (wappuoutput != None):
                        wappuoutput = '{:s}:n Wappua on kulunut {:s}'.format(user[0].lstrip(':'), wappuoutput)
                        socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))
                    else:
                        wappuoutput = '{:s}:n Wappu ei ole vielä alkanut.'.format(user[0].lstrip(':'))
                        socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], wappuoutput).encode('utf-8'))

            elif (response[3] == ':!setwappu'):
                if (len(response) > 4):
                    pattern = re.compile('([0-9]{1,2}[.]){2}[0-9]{4}')
                    pattern2 = re.compile('([0-9]{2}:){2}[0-9]{2}')
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
                        glVal['wapputimes'][user[1]] = outputdict
                        outputstring = ':n Wappu alkoi {:d}.{:d}.{:d} {:d}:{:d}:{:d}'.format(wappudate[0], wappudate[1], wappudate[2], wapputime[0], wapputime[1], wapputime[2])
                        socket.send('PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0].lstrip(':'), outputstring).encode('utf-8'))
                        writeConfig()
                
                else:
                    wappudate = datetime.now()
                    wappuoutput = '{0},{1},{2},{3},{4},{5}'.format(wappudate.year, wappudate.month, wappudate.day, wappudate.hour, wappudate.minute, wappudate.second)
                    glVal['wapputimes'][user[1]] = wappuoutput
                    outputstring = ':n Wappu alkoi {:d}.{:d}.{:d} {:d}:{:d}:{:d}'.format(wappudate[0], wappudate[1], wappudate[2], wapputime[0], wapputime[1], wapputime[2])
                    socket.send('PRIVMSG {:s} :{:s}{:s}\r\n'.format(response[2], user[0], outputstring).encode('utf-8'))
                    writeConfig()

            elif (response[3] == ':!juhannus'):
                socket.send('PRIVMSG {:s} :{:s}\r\n'.format(response[2], getJuhannus()).encode('utf-8'))

            if (isFaggot):
                print('homohommat')
                pattern = re.compile('(.*http.://.*)|(.*www[.].*)|(.*pornhub[.]com.*)')
                print(pattern.match(message))
                if (pattern.match(message)):
                    socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#pornonystavat', 'Ha, gayyyyy!').encode('utf-8'))
                    #socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#otit.bottest', 'Ha, gayyyyy!').encode('utf-8'))
                    print('Sent messsage to server')
            
            pattern = re.compile('.*talo.*')
            # print('user[0] == fonillius1: {:b}'.format(user[0] == ':fonillius1'))
            # print('pattern.match(message): {:s}'.format(pattern.match(message)))
            if (user[0] == ':fonillius1' and pattern.match(message)):
                socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#oty', 'yksityistilaisuus').encode('utf-8'))
                #socket.send('PRIVMSG {:s} :{:s}\r\n'.format('#otit.bottest', 'yksityistilaisuus').encode('utf-8'))


        except KeyboardInterrupt:
            print('\nGoodbye')
            return None
        
        #except:
        #   pass


if __name__ == '__main__':
    
    IPaddress = 'open.ircnet.net'
    #IPaddress = 'irc.oulu.fi'
    portNo = 6667

    """
    nick = 'BOTSebbu'
    username = 'BOTSebbu'
    realname = 'Pornon ystaevae'
    hostname = 'IRC'
    servername = 'IRCnet'

    """

    nick = 'TestSebbu'
    username = 'TestSebbu'
    realname = 'Debuggaamisen ystaevae'
    hostname = 'IRC'
    servername = 'IRCnet'
    

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((IPaddress, portNo))

    print('Connected to {:s}'.format(IPaddress))
    
    clientSocket.send('USER {:s} {:s} {:s} :{:s}\r\n'.format(username, hostname, servername, realname).encode('utf-8'))
    clientSocket.send('NICK {:s}\n'.format(nick).encode('utf-8'))

    #clientSocket = joinChannel(clientSocket, ['#sebbutest', '#pornonystavat', '#otit.2016', '#olto'])
    clientSocket = joinChannel(clientSocket, ['#sebbutest'])

    
    readConfig()
    """
    try:
        readConfig()
    except:
        pass
    """

    runloop(clientSocket)
    clientSocket.close()

else:
    print('pass')
