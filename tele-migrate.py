from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerUser, InputPeerEmpty, PeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, FloodWaitError, PeerIdInvalidError, ChatAdminRequiredError
import time
import sys
import csv
import traceback

class TGUser:
    def __init__(self, userId, access_hash, name, surname, username):
        self.id = userId
        self.access_hash = access_hash
        self.first_name = name
        self.last_name = surname
        self.name = self.first_name + (" " + self.last_name if self.last_name else "")
        self.username = username
    
    def __str__(self):
        out = ""
        out = out + str(self.id) + ","
        out = out + str(self.access_hash) + ","
        out = out + self.name + ","
        out = out + (str(self.username) if self.username else "")
        return out

    def __eq__(self, other):
        if isinstance(other, TGUser):
            return other.id == self.id and other.access_hash == self.access_hash and other.first_name == self.first_name and other.last_name == self.last_name and other.username == self.username
        else:
            return False
    
    def __hash__(self):
        return hash(str(self))

apiID = #<Insert your Telegram API ID here>
apiHash = #<Insert your Telegram API hash here>
phone = #<Insert your Telegram phone number here>

helpMessage = (
    f"Usage: python(3) {sys.argv[0]} [command]\n"
    f"Possible commands:\n"
    f"save - store to a file the details of all users in source group and not in destination group\n"
    f"message - send a message to all users in source group and not in destination group"
)

try:
    operation = sys.argv[1]
except IndexError:
    raise SystemExit(helpMessage)

if operation != "save" and operation != "message":
    #Display help message and quit
    raise SystemExit(helpMessage)
else:
    #### Setup
    client = TelegramClient(phone, apiID, apiHash)
    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input("Enter the code you just recieved: "))

    groups = [d.entity
        for d in client.get_dialogs()
        if d.is_channel]

    users = {}
    confirmed = False
    while not confirmed:
        try:
            # Print all groups this user has access to and ask for source and target groups
            for i, g in enumerate(groups):
                print(str(i) + " - " + g.title + " - Members: " + str(g.participants_count))
            sourceGroupIndex = input("Enter the number of the SOURCE group: ")
            targetGroupIndex = input("Enter the number of the TARGET group: ")

            sourceGroup = groups[int(sourceGroupIndex)]
            targetGroup = groups[int(targetGroupIndex)]

            sourceUsers = client.get_participants(sourceGroup, aggressive=True)
            sourceUsersDict = [TGUser(u.id, u.access_hash, u.first_name, u.last_name, u.username) for u in sourceUsers]
            targetUsers = client.get_participants(targetGroup, aggressive=True)
            targetUsersDict = [TGUser(u.id, u.access_hash, u.first_name, u.last_name, u.username) for u in targetUsers]

            users = set(sourceUsersDict) - set(targetUsersDict)

            # Change confirmation message based on the operation chosen on command line
            if operation == "save":
                confirmationMessage = (
                    f"Saving all users in {sourceGroup.title} "
                    f"and not in {targetGroup.title} "
                    f"to a csv file. Is this ok? [y/N]: "
                )
            else:
                message = input("Enter message to send: ")
                confirmationMessage = (
                    f"Sending '{message}' to all users in {sourceGroup.title} "
                    f"and not in {targetGroup.title}. "
                    f"Is this ok? [y/N]: "
                )
            confirmationResponse = input(confirmationMessage)
            confirmed = confirmationResponse == "y" or confirmationResponse == "Y"
        except ChatAdminRequiredError:
            print("Admin privileges needed to access user list for this chat/channel.")
            continue
        except PeerIdInvalidError:
            client.disconnect()
            raise SystemExit("Getting Peer Id Invalid Error from Telegram. Exiting.")
        except Exception:
            tracebackStr = traceback.format_exc()
            print(tracebackStr)
            client.disconnect()
            raise SystemExit("A fatal error occurred. Exiting")

    if operation == "save":
        print('Saving to csv file...')
        with open("membersInSourceGroupNotTarget.csv","w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",",lineterminator="\n")
            writer.writerow(['user id', 'access hash', 'name', 'username'])
            for user in users:
                if user.username:
                    username = user.username
                else:
                    username = ""
                if user.first_name:
                    first_name = user.first_name
                else:
                    first_name = ""
                if user.last_name:
                    last_name= user.last_name
                else:
                    last_name = ""
                name = (first_name + " " + last_name).strip()
                writer.writerow([user.id, user.access_hash, name, username])

        print('Members saved to csv file successfully.')
        client.disconnect()
    else:
        # Send message to everyone in the users set
        sleepTime = 15

        for i, u in enumerate(users):
            try:
                #To avoid FloodWaitError, wait a while between each batch of 50 messages
                if (i + 1) % 50 == 0:
                    print("Messaged 50 users. Waiting 15 minutes.")
                    time.sleep(900)

                userID = u.id
                accessHash = u.access_hash
                username = u.username
                name = u.name

                recipient = InputPeerUser(userID, accessHash)

                print(f"Sending message to: {name}")
                client.send_message(recipient, message)
                print(f"Waiting {sleepTime} seconds")       
                time.sleep(sleepTime)
            except FloodWaitError as e:
                tracebackStr = traceback.format_exc()
                print(tracebackStr)
                client.disconnect()
                raise SystemExit(f"Must wait for {e.seconds} before sending more messages.")
            except PeerFloodError:
                tracebackStr = traceback.format_exc()
                print(tracebackStr)
                client.disconnect()
                raise SystemExit("Getting Flood Error from Telegram. Exiting. Please wait a while before trying again.")
            except Exception:
                tracebackStr = traceback.format_exc()
                print(tracebackStr)
                client.disconnect()
                raise SystemExit("A fatal error occurred. Exiting")
        
        print("Message sent to all users successfully.")
        client.disconnect()
