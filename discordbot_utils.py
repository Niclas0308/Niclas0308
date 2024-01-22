import discord
import json
import datetime
import requests
import os

#getting userinfo: message content, avatar as a link, authorname
def getUserInfo(message):
    messageByUser = message.content
    avatarOfUser = message.author.avatar
    author = message.author

    return messageByUser, avatarOfUser, author

#editing the Changelog message made by the user
def editChangelogMessage(messageByUser):
    user_message = {
        "message": messageByUser
        }

    #slicing messageByUser into pieces to make them fit into subcategories
    ReplacementArray = ["Where changed:", "Why changed:", "Note:"]
    for word in ReplacementArray:
        user_message["message"] = user_message["message"].replace(word, "splitme")
    user_message["message"] = user_message["message"].split("splitme")
    c_what = user_message["message"][0].replace("What changed:", "")
    c_where = user_message["message"][1]
    c_why = user_message["message"][2]
    c_note = user_message["message"][3]

    return c_what, c_where, c_why, c_note


def editExistingData(event_name, event_description, event_time, event_max_participants, event_picture, creatorMessageID):
    with open("events.json", "r") as event_edited_data:
        data = json.load(event_edited_data)
    index = 0
    for i in range(0, len(data["events"])):
        if data["events"][i]["creator_message_id"] == creatorMessageID:
            index = i
            
            data["events"][index]["event_name"] = event_name
            data["events"][index]["event_description"] = event_description
            data["events"][index]["event_time"] = event_time
            data["events"][index]["event_max_participants"] = event_max_participants
            data["events"][index]["picture"] = event_picture
            break

    with open("events.json", "w") as event_edited_data:
        json.dump(data, event_edited_data, indent=4)
    
    return data["events"][index]


#preparing the event message made by the user
def preparingEventMessage(messageToEvent):
    is_Int = True
    user_message = {
        "message": messageToEvent
        }
    print("before for-loop: " + str(messageToEvent))
    #slicing messageByUser into pieces to make them fit into subcategories
    ReplacementArray = ["What is planned:", "Max participants:", "Time:", "Picture:"]
    for word in ReplacementArray:
        user_message["message"] = user_message["message"].replace(word, "splitme")
    user_message["message"] = user_message["message"].split("splitme")

    event_name = user_message["message"][0].replace("Event name:", "")
    event_description = user_message["message"][1]
    if isInt(user_message["message"][2]) == False:
        is_Int = False
        event_max_participants = False
    else:
        event_max_participants = user_message["message"][2]
    event_time = user_message["message"][3]
    event_picture = user_message["message"][4]

    return event_name, event_description, event_time, event_max_participants, event_picture

def isInt(value):
    try:
        int(value)  # Try to typecast the value to int
        return True
    except (ValueError, TypeError):
        return False
    
def makeNewEventInJson(event_name, event_description, event_time, event_max_participants, event_picture, creator):
    with open("events.json", "r") as event_data:
        data = json.load(event_data)
        event_id = len(data["events"])
        creator = str(creator.id)
        taggableCreator = "<@" + str(creator) + ">"


        newEvent = {
            "event_id": event_id,
            "event_name": event_name,
            "event_description": event_description,
            "event_time": event_time,
            "event_max_participants": event_max_participants,
            "picture": event_picture,
            "creator": creator,
            "creator_message_id": 0,
            "preview_message_id": 0,
            "published_message_id": 0,
            "newEventChannelID": 0,
            "signups": [
            ]
        }
        
        with open("events.json", "w") as event_data:    
            data["events"].append(newEvent)
            json.dump(data, event_data, indent=4)
    return data["events"][event_id]


def addPlayerToEvent(user_id, published_message_id):
    with open("events.json", "r") as event_data:
        data = json.load(event_data)
        index = 0
        isAdded = False
        emptySlot = False
        for i in range(0, len(data["events"])):
            if data["events"][i]["published_message_id"] == published_message_id:
                #if len(data["events"][i]["signups"]) < int(data["events"][i]["event_max_participants"]):    
                index = i
                isSignedup = False
                #checking if there is still a free signup slot
        for k in range(len(data["events"][index]["signups"])):
            print(data["events"][index]["signups"][k]["player" + str(k)] == "")
            if data["events"][index]["signups"][k]["player" + str(k)] == "":
                    emptySlot = True
                    freeSlotIndex = k
                    break
        #checking if player is already signed up
        for j in range(len(data["events"][i]["signups"])):
            if "<@" + str(user_id) + ">" == data["events"][index]["signups"][j]["player" + str(j)]:
                    isSignedup = True
                    break
        if emptySlot == True and isSignedup == False:
            data["events"][index]["signups"][freeSlotIndex]["player" + str(freeSlotIndex)] = "<@" + str(user_id) + ">"
            isAdded = True
            with open("events.json", "w") as event_file:
                json.dump(data, event_file, indent=4)
        if isAdded == True:
            return user_id, data["events"][index]
        else:
            print(str(isSignedup) + " " + str(emptySlot)) 
            return False
                    

def savetoEventsJson(event_id, targetInEvents, dataToSave):
    with open("events.json", "r") as event_data:
        data = json.load(event_data)
        for i in range(0, len(data["events"])):
            if data["events"][i]["event_id"] == event_id:
                data["events"][i][targetInEvents] = dataToSave
                break
    
    with open("events.json", "w") as event_data:
        json.dump(data, event_data, indent=4)


def getMessageInfo(message_id):
    with open("events.json", "r") as events_file:
        data = json.load(events_file)
    messageData = data
    for i in range(len(data["events"])):
        if data["events"][i]["published_message_id"] == message_id:
            messageData = data["events"][i]
            break
    
    return messageData

def getMessageInfobyEventID(event_id):
    with open("events.json", "r") as events_file:
        data = json.load(events_file)
    messageData = data
    for i in range(len(data["events"])):
        if data["events"][i]["event_id"] == event_id:
            messageData = data["events"][i]
            break
    
    return messageData

def removePlayerFromEvent(user_id, published_message_id):
    with open("events.json", "r") as event_file:
        event_data = json.load(event_file)
        isSignedOut = False
    for i in range(len(event_data["events"])):
        if isSignedOut == True:
            break
        if event_data["events"][i]["published_message_id"] == published_message_id:
            index = i
            for j in range(len(event_data["events"][i]["signups"])):
                if event_data["events"][i]["signups"][j]["player" + str(j)] == "<@" + str(user_id) + ">":
                    event_data["events"][i]["signups"][j]["player" + str(j)] = ""
                    isSignedOut = True
                    event_file.close()
                    
                    with open("events.json", "w") as event_file1:
                        json.dump(event_data, event_file1, indent=4)
                    break

    if isSignedOut == True:
        return user_id, event_data["events"][index]
    else:
        return False
    
def deleteEventEntry(event_id):
    with open("events.json", "r") as event_file:
        data = json.load(event_file)
    
    for i in range(len(data["events"])):
        if data["events"][i]["event_id"] == event_id:
            del data["events"][i]

    with open("events.json", "w") as event_new:
        json.dump(data, event_new, indent=4)

def addPlayerEntries(event_max_participants, event_id):
        with open("events.json", "r") as player_file:
            newEvent = json.load(player_file)
        index = 0
        for j in range(len(newEvent["events"])):
            if newEvent["events"][j]["event_id"] == event_id:
                index = j
        for i in range(int(event_max_participants)):
            newPlayer = { "player" + str(i): "" }
            newEvent["events"][index]["signups"].append(newPlayer)

        with open("events.json", "w") as event_file:
            json.dump(newEvent, event_file, indent=4)

def datestrToDateUnix(timestamp_str):

    # Convert the timestamp string to a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)

    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(timestamp.timestamp())
    unix_timestamp_discord = "<t:" + str(unix_timestamp) + ":f>"

    return unix_timestamp_discord

def getEventIDByEventChannelID(eventchannel_id):
    with open("events.json", "r") as event_edited_data:
        data = json.load(event_edited_data)
    index = 0
    for i in range(0, len(data["events"])):
        if data["events"][i]["newEventChannelID"] == eventchannel_id:
            index = i
            break
    
    return data["events"][index]["event_id"]

#adds new entry to warnings
def addNewWarning(user_id, reason, moderator, proof):
    if proof == None:
        proof = ""
    wasAdded = False
    index = 0
    with open("warnings.json", "r") as warnings_read:
        warnings_data = json.load(warnings_read)
    
    isExisting = False
    for i in range(len(warnings_data["warnings"])):
        if warnings_data["warnings"][i]["user_id"] == user_id:
            isExisting = True
            newWarning = { 
                    1: "" + str(reason), 
                    "by": "" + str(moderator),
                    "proof": "" + str(proof)
                }
            warnings_data["warnings"][i]["warnings"].append(newWarning)
            break
    
    if isExisting == False:
        newWarning = {
                "user_id": user_id,
                "warnings": [
                    {
                        1: "" + str(reason),
                        "by": "" + str(moderator),
                        "proof": "" + str(proof)
                    }
                ]
            }
        warnings_data["warnings"].append(newWarning)
    with open("warnings.json", "w") as warnings_write:
        json.dump(warnings_data, warnings_write, indent=4)
    if isExisting == False:
        return newWarning["warnings"][0]
    else: 
        return newWarning

def getWarnings(user_id):
    with open("warnings.json", "r") as warnings_read:
        warnings_data = json.load(warnings_read)
    index = 0
    isFound = False
    for i in range(len(warnings_data["warnings"])):
        if warnings_data["warnings"][i]["user_id"] == user_id:
            index = i
            isFound = True
    if isFound == True:
        return warnings_data["warnings"][index]
    if isFound == False:
        addToDatabase = {
            "user_id": 281554193964072970,
            "warnings": []
        }
        warnings_data["warnings"].append(addToDatabase)
        with open("warnings.json", "w") as warnings_write:
            json.dump(warnings_data, warnings_write, indent=4)
        return addToDatabase

def removeWarning(user_id, warning_number):
    with open("warnings.json", "r") as warnings_read:
        warnings_data = json.load(warnings_read)
    isFound = False
    for i in range(len(warnings_data["warnings"])):
        if warnings_data["warnings"][i]["user_id"] == user_id:
            removedWarning = warnings_data["warnings"][i]["warnings"][warning_number-1]
            del warnings_data["warnings"][i]["warnings"][warning_number-1]
            isFound = True
            with open("warnings.json", "w") as warnings_write:
                json.dump(warnings_data, warnings_write, indent=4)
            break
    if isFound == True:
        return removedWarning
    else:
        return False

def getPermissions(role):
    with open("permissions.json", "r") as perms_read:
        perms_data = json.load(perms_read)
    index = 0
    isFound = False
    if isInt(role) == False:
        for i in range(len(perms_data["roles"])):
            if perms_data["roles"][i]["role_name"] == role:
                index = i
                isFound = True
                break

    if isInt(role) == True:
        for i in range(len(perms_data["roles"])):
            if perms_data["roles"][i]["role_id"] == role:
                index = i
                isFound = True
                break
    
    if isFound == True:
        return perms_data["roles"][index]
    else: 
        return False
    
def hasRole(member, role_name):
    # Get the role object by name
    role = discord.utils.get(member.guild.roles, name=role_name)
    
    if role in member.roles:
        return True
    else:
        return False

def checkPermissions(member, roles, permission):
    isJusticar = False
    if hasRole(member, roles[0]) == True:
        isJusticar = True
        perms_data = getPermissions(roles[0])
        if perms_data == False or perms_data["perms"][0][permission] == False:
            return roles[0], False
        if perms_data != False and perms_data["perms"][0][permission] == True:
            return roles[0], True


    if hasRole(member, roles[1]) == True and isJusticar == False:
        perms_data = getPermissions(roles[1])
        if perms_data == False or perms_data["perms"][0][permission] == False:
            return roles[1], False
        if perms_data != False and perms_data["perms"][0][permission] == True:
            return roles[1], True

def download_image(url, save_directory=None):
    save_directory = "img"
    try:
        # Send an HTTP GET request to fetch the image
        response = requests.get(url, stream=True)

        # Check if the request was successful
        response.raise_for_status()

        # Extract the filename from the URL
        filename = url.split("/")[-1]

        # Define the complete file path to save the image
        save_path = os.path.join(save_directory, filename)

        # Open the file in binary write mode and save the image content
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Image downloaded successfully and saved as '{save_path}'")
        return filename
    except requests.exceptions.HTTPError as e:
        print(f"Error downloading the image: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")