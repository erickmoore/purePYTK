from purestorage import purestorage
import sys
import requests

# Disable certificate warnings

requests.packages.urllib3.disable_warnings()

# Set variables

array_name = ""
array_api = ""
new_vol_prefix = "test-clone-"

# Initialize variables

new_line = '\n'
snap_lst = []
snap_set = set()
pgroup_lst = []

# Prompt to set variables if null

if array_name == "":
    print(new_line + "Please edit the script to include the FlashArray FQDN or management IP." + new_line)
    sys.exit()

if array_api == "":
    print(new_line + "Please edit the script to include the FlashArray API key." + new_line)
    sys.exit()

# Login to the Flash array

try:
    print(new_line + "Connecting to: " + array_name + new_line)
    array = purestorage.FlashArray(array_name, api_token=array_api)

except:
    print(new_line + "Something happened, we can't connect to the array!")
    print("Please check network and array settings." + new_line)
    sys.exit()

# Build function for displaying list output

def choices(list_data, itemName):

    listNum = 0
    global myChoice
    myChoice = ""

    while myChoice == "":
        for item in list_data:
            print("[" + str(listNum) + "]" + item)
            listNum += 1

        try:
            myChoice = int(input(new_line + "Choose a " + itemName + " from the list:"))
            print(new_line)

        except:
            print(new_line + "No/invalid input or (CTRL-C); exiting stage left." + new_line)
            sys.exit()

        else:
            if myChoice >= listNum:
                print("No matching " + itemName + "; please try again." + new_line)
                listNum = 0
                myChoice = ""
                continue

# Find all protection groups and prompt for a selection

pgroups = array.list_pgroups()

for current_pgroup in pgroups:
    pgroup_lst.append(current_pgroup['name'])

# Call function to build a prompt

choices(pgroup_lst,"Protection Group")

pgroup_name = pgroup_lst[myChoice]
print(new_line + "Looking for snapshots in: " + pgroup_name + new_line)

# Find all volumes with named protection group snapshots

pgroup_snaps = array.list_volumes(snap="true", pgrouplist=[pgroup_name])

# Loop through all volumes and add them to a list containing the snapshot name and number

for current_pgroup in pgroup_snaps:
    snap_name = str(current_pgroup['name'].split(".")[0]) + "." + str(current_pgroup['name'].split(".")[1])
    snap_set.add(snap_name)

# Sort by most recent snap and change set to list

snap_lst = list(snap_set)
snap_lst.sort(reverse=True)

# Call function to build a prompt

choices(snap_lst, "SnapShot")
print(new_line)

# Set the snapshot number to the number chosen at the commmand prompt and print the choice

snapNum = snap_lst[myChoice]
print("Starting copy from snapshot: " + snapNum + new_line)

# Set snapNum variable equal to the chosen snapshot number

snapNum = snapNum.split(".")[1]

# Loop through all volumes in chosen snapshot and create clones

for volume in pgroup_snaps:
    if volume['name'].split(".")[1] == snapNum:
       copyName = new_vol_prefix + str(volume['name'].split(".")[2])
       print("Creating clone from volume: " + str(volume['name'].split(".")[2]))
       array.copy_volume(volume['name'],copyName)

print(new_line + "All done, enjoy your zero space copies!" + new_line)

array.invalidate_cookie()
