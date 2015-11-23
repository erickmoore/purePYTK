from purestorage import purestorage
import sys
import requests

#Disable certificate warnings

requests.packages.urllib3.disable_warnings()

# Set variables

arrayName = ""
arrayAPI = ""
newLine = '\n'
tab = '\t'

# Prompt to set variables if null

if arrayName == "":
    print(newLine + "Please edit the script to include the FlashArray FQDN or management IP." + newLine)
    sys.exit()

if arrayAPI == "":
    print(newLine + "Please edit the script to include the FlashArray API key." + newLine)
    sys.exit()

# Login to the Flash array

try:
    print(newLine + "Connecting to: " + arrayName + newLine)
    array = purestorage.FlashArray(arrayName, api_token=arrayAPI)

except:
    print(newLine + "Something happened, we can't connect to the array!")
    print("Please check network and array settings." + newLine)
    sys.exit()

# Build function for displaying list output

def choices(listData, itemName):

    listNum = 0
    global myChoice
    myChoice = ""

    while myChoice == "":
        for item in listData:
            print("[" + str(listNum) + "]" + item)
            listNum += 1

        try:
            myChoice = int(input(newLine + "Choose a " + itemName + " from the list:"))
            #print("You chose: " + myChoice)
            print(newLine)

        except:
            print(newLine + "No/invalid input or (CTRL-C); exiting stage left." + newLine)
            sys.exit()

        else:
            if myChoice >= listNum:
                print("No matching " + itemName + "; please try again." + newLine)
                listNum = 0
                myChoice = ""
                continue


#Zero out counter variables

total_reads = 0
total_writes = 0
total_iops = 0
hostNameset = set()
myItteration = 0

allHosts = array.list_hosts()

for currentHost in allHosts:
    hostNameset.add(currentHost['name'])

choices(hostNameset, "host name")

#Get command line argument for host name

selectedHost = allHosts[myChoice]['name']

hostVols = array.list_host_connections(selectedHost)

#Find all volumes attached to host and then pull volume performance data

print("host name" + tab + tab + "total_iops" + tab + "read_iops" + tab + "write_iops")

while myItteration < 30:

    total_reads = 0
    total_writes = 0
    total_iops = 0

    for current in hostVols:
        currentVol = current['vol']
        myVol = array.get_volume(currentVol, action="monitor")

        for activeVol in myVol:
            total_reads = total_reads + activeVol['reads_per_sec']
            total_writes = total_writes + activeVol['writes_per_sec']


    total_iops = total_writes + total_reads

    print(selectedHost + tab + tab + str(total_iops) + tab + tab + str(total_reads) + tab + tab + str(total_writes))

    myItteration += 1

array.invalidate_cookie()
