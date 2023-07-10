import re
import sys
import discord
import signal
import os
import threading
from sys import argv
from datetime import datetime

bifrostIOC = 'MjolnirKeyL:'
TOKENPATTERN = r'TOKEN = \"(.*)\"'
PYPATTERN = r'\.py.*'
fileContents = ''
maliciousPIDS = []
found = False


def taskList(file):
    pids = []
    exceptionFolders = ['sys', 'tty', 'bus']
    if sys.platform == 'win32':
        try:
            output = os.popen('wmic process get description, commandline, processid').readlines()

            for line in output:
                if line != '':
                    for arg in line.split():
                        if file in arg:
                            print(line.split())
                            pids.append(line.split()[-1])
        except:
            print('[!] Unable to get processes')

    else:
        for proc in os.listdir('/proc'):
            if os.path.isdir('/proc/' + proc) and proc not in exceptionFolders and not os.path.islink('/proc/' + proc):
                with open('/proc/' + proc + '/cmdline', 'r') as f:
                    if file in f.read():
                        pids.append(proc)
    return pids


def killBifrost(pids):
    for i in pids:
        try:
            os.kill(int(i), signal.SIGTERM)
        except:
            print(f'[!] Unable to kill process running with PID {i}')


for root, dirs, files in os.walk("."):
    if found:
        break
    path = root.split(os.sep)
    for file in files:
        if found:
            break
        if re.findall(PYPATTERN, file):
            try:
                with open(os.path.join(root, file), 'r') as f:
                    fileContents = f.read()
                    # print(list(set(f.read().split(' ')) & set(bifrostIOCs)))
                    if bifrostIOC in fileContents and os.path.abspath(file) != os.path.normpath(argv[0]):
                        clientPath = os.path.join(root, file)
                        client = file
                        # fileContents = f.read()
                        print(f'[*] Client file: {client}')
                        print(f'[*] Client path: {clientPath}')

                        found = True
                        break
            except:
                pass
if re.findall(TOKENPATTERN, fileContents):
    TOKEN = re.findall(TOKENPATTERN, fileContents)[0]
    print(f'[*] Scraped Token: {TOKEN}')
    maliciousPIDS = taskList(client)

else:
    print('[!] Bifrost was not found on this system...')

try:
    os.rename(clientPath, clientPath + '.bak')
    print(f'[*] Bifrost client renamed to {clientPath + ".bak"}')
except:
    print(f'[!] Unable to rename file at {clientPath}')

print(f'[*] Malicious PIDs: {", ".join(maliciousPIDS)}')
killBifrost(maliciousPIDS)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == client.user:
        return
    received_message = message.content
    print(f'\r{message.author}: "{received_message}" - {datetime.now()}')
    if received_message.startswith('%'):
        await message.channel.send('I LIVE IN YOUR WALLS I AM EATING YOUR DRYWALL')
clientThread = threading.Thread(target=client.run, args=(TOKEN,), daemon=True)
clientThread.start()
# client.run(TOKEN)

try:
    input('> ')
except KeyboardInterrupt:
    sys.exit()

