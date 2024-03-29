import os
import dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import database
import requests
import threading
import re
import json

import send_unlock_message
import send_snacc_message
import download_file
import unlock_drawer

workspace_core_channel_id = "C03RXCV2FP0"

def get_plurality(number):
    if number == 1:
        return "credit"
    else:
        return "credits"

def load_json_template(file_path, **kwargs):
    with open("Messages/" + file_path, 'r') as file:
        template = file.read()
        return json.loads(template)
    
def user_is_workspace_manager(client, user_id):
    #get list of members in #workspace-core

    response = client.conversations_members(channel=workspace_core_channel_id)

    members = response['members']

    if user_id in members:
        return True
    else:
        return False

# Load environment variables
dotenv.load_dotenv()

# Initialize the Bolt app
app = App(
    token=os.environ.get('SLACK_BOT_TOKEN')
)

# Create the database when the script is run
database.create_database()

@app.command("/snacc")
def snacc_command(ack, body, client, command, respond):

    # Acknowledge the command request
    ack()

    # Get user ID from the command request
    user_id = body['user_id']

    # Get the profile picture of the user
    user_info = client.users_info(user=user_id)
    user_picture = user_info['user']['profile']['image_192'] 

    send_snacc_message.send_snacc_message(user_id, user_picture, client)
    
@app.command("/snack")
def snack_command(ack, body, client, command, respond):
    ack()

    user_id = body['user_id']

    print(user_id)

    credits = database.get_user_credits(user_id)

    if credits > 0:
        send_unlock_message.send_unlock_ephemeral(user_id, credits, client, respond)
        
    else:
        respond(
            text="You have 0 credits. Clean for 5 minutes, then send a photo to <@U05T96UN4NN> to earn a credit. See <https://ssi-wiki.stanford.edu/Snack_Bot|the wiki> for more info."
        )

@app.command("/workspace-unlock-snack-cabinet")
def snack_command(ack, body, client, command, respond):   
    ack()

    user_id = body['user_id']

    if user_is_workspace_manager(client, user_id):
        thread = threading.Thread(target=unlock_drawer.unlock_all, args=())
        thread.start()

        respond(
            text="The cabinets have been unlocked. They will lock automatically in 5 minutes"
        )

    else:
        respond(
            text="You are not authorized to use this command."
        )

def extract_user_ids(text):
    pattern = r"<@([A-Z0-9]+)\|"
    return re.findall(pattern, text)

def extract_numbers(text):
    number_pattern = r"\b\d+\b"
    numbers = re.findall(number_pattern, text)
    return numbers

@app.command("/workspace-add-snack-credits")
def snack_command(ack, body, client, command, respond):
    ack()

    if user_is_workspace_manager(client, body['user_id']):
        user_ids = extract_user_ids(body['text'])

        numbers = extract_numbers(body['text'])
        if len(numbers) > 0 and (len(numbers) > 1 or int(numbers[0]) > 9):
            respond(
                text="Cannot parse. Please enter only user tags and a number between 1 and 9 for the number of credits (or blank for one credit)."
            )
            return
        
        credits_to_add = int(numbers[0]) if len(numbers) > 0 else 1

        users_added_string = ""
        for user_id in user_ids:
            database.update_user_credits(user_id, credits_to_add)
            new_credits = database.get_user_credits(user_id)
            users_added_string += f"<@{user_id}>\n"
            client.chat_postMessage(
                channel=user_id,
                text=f"You have been given {credits_to_add} {get_plurality(credits_to_add)} by <@{body['user_id']}>. You now have {new_credits} {get_plurality(new_credits)}. You can use them to redeem snack in the break room with `/snack`."
            )

        respond(
            text=f"{credits_to_add} {get_plurality(credits_to_add)} given to the following users:\n" + users_added_string
        )
        
    else:
        respond(
            text="You are not authorized to use this command."
        )

@app.command("/workspace-refresh-snack-credits")
def snack_command(ack, body, client, command, respond):
    ack()

    if user_is_workspace_manager(client, body['user_id']):
        database.refresh_free_credits()
        respond(
            text="Free credits have been refreshed."
        )
    else:
        respond(
            text="You are not authorized to use this command."
        )

@app.event("file_shared") # User posts a photo of a clean area
def handle_file_upload(event, client, logger):
    user_id = event['user_id'] 
    file_id = event['file_id'] 
    channel_id = event['channel_id']
    snackbot_pics_channel_id = "C06BLHGG5GX"

    if channel_id.startswith('D'):  # Check if the file is uploaded in a DM

        file_data = client.files_info(file=file_id)
        file_url = file_data['file']['url_private_download']

        # Download the file
        file = download_file.download_file(file_url, os.environ.get('SLACK_BOT_TOKEN'))

        #post the file to the channel
        response = client.files_upload(
            channels=snackbot_pics_channel_id,
            file=file,
            initial_comment=f"<@{user_id}> earned a credit!"
        )

        database.update_user_credits(event['user_id'], 1)

        credits = database.get_user_credits(user_id)

        #reacts to the file
        client.reactions_add(channel = snackbot_pics_channel_id, name = "not-clean", timestamp = response['file']['shares']['public'][snackbot_pics_channel_id][0]['ts'])

        send_unlock_message.send_unlock_message(user_id, credits, client, "Thanks for cleaning!")

def unlock_cabinet(cabinet, body):
    response_url = body["response_url"]
    user_id = body['user']['id']
    credits = database.get_user_credits(user_id)

    #double check that the user still has enough credits
    if credits == 0:
        requests.post(response_url, json={
            "replace_original": "true",
            "text": "You have 0 credits. Clean for 5 minutes, then send a photo to <@U05T96UN4NN> to earn a credit. See <https://ssi-wiki.stanford.edu/Snack_Bot|the wiki> for more info."
        })
        return
        
    thread = threading.Thread(target=unlock_drawer.unlock_shelf, args=(cabinet,))
    thread.start()
    database.use_credit(user_id)

    requests.post(response_url, json={
        "replace_original": "true",
        "text": f"{cabinet.name.capitalize()} cabinet has been unlocked! You now have {credits - 1} {get_plurality(credits-1)} left."
    })

@app.action("unlock_1")
def handle_unlock_1(ack, body, client, logger):
    ack()
    unlock_cabinet(unlock_drawer.Shelf.TOP, body)
    

@app.action("unlock_2")
def handle_unlock_2(ack, body, client, logger):
    ack()
    unlock_cabinet(unlock_drawer.Shelf.MIDDLE, body)

@app.action("unlock_3")
def handle_unlock_3(ack, body, client, logger):
    ack()
    unlock_cabinet(unlock_drawer.Shelf.BOTTOM, body)

@app.action("save_credit")
def handle_save_credit(ack, body, client, logger):
    ack()

    response_url = body["response_url"]
    user_id = body['user']['id']
    credits = database.get_user_credits(user_id)

    requests.post(response_url, json={
        "replace_original": "true",
        "text": f"Credit saved. You have {credits} {get_plurality(credits)}."
    })

@app.event("reaction_added")
def handle_reaction(ack, event, client):
    ack()
    print("Reaction added: ")

    specific_emoji = "not-clean" 
    target_channel = workspace_core_channel_id

    # Check if the reaction is the one you're interested in
    if event["reaction"] == specific_emoji:
        # Get the message details
        channel_id = event["item"]["channel"]
        message_ts = event["item"]["ts"]

        reacting_user = event["user"]

        # Share the message to the target channel
        if channel_id == "C06BLHGG5GX":
            try:
                result = client.chat_getPermalink(
                    channel=channel_id,
                    message_ts=message_ts
                )
                permalink = result.get("permalink")

                # Post the message permalink to the target channel
                client.chat_postMessage(
                    channel=target_channel,
                    text=f"<@{reacting_user}> reported a photo: {permalink}"
                )
            except Exception as e:
                print(f"Error in sharing the message: {e}")    
    

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
