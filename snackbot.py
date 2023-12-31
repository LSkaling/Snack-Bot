import os
import dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import sqlite3
import asyncio
import requests

import subprocess

import json

def load_json_template(file_path, **kwargs):
    with open("Messages/" + file_path, 'r') as file:
        template = file.read()
        return json.loads(template.format(**kwargs))

def execute_gpio_control(pin, duration):
    # Command to run the GPIO control script
    command = ['python', 'gpio_controller.py', str(pin), str(duration)]

    # Run the command in a separate process
    subprocess.Popen(command)

def create_database():
    # Connect to SQLite DB (it will be created if it doesn't exist)
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credits (
            user_id TEXT PRIMARY KEY,
            credits INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# create_database()
# print("Database created")

def update_user_credits(user_id, credits):
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    # Check if the user already exists
    cursor.execute("SELECT credits FROM user_credits WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        # Insert new user
        cursor.execute("INSERT INTO user_credits (user_id, credits) VALUES (?, ?)", (user_id, credits))
    else:
        # Update existing user
        new_credits = result[0] + credits
        cursor.execute("UPDATE user_credits SET credits = ? WHERE user_id = ?", (new_credits, user_id))

    conn.commit()
    conn.close()

def get_user_credits(user_id):
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    # Check if the user already exists
    cursor.execute("SELECT credits FROM user_credits WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        return 0
    else:
        return result[0]

# Load environment variables
dotenv.load_dotenv()

# Initialize the Bolt app
app = App(
    token=os.environ.get('SLACK_BOT_TOKEN')
)

@app.command("/snacc")
def snacc_command(ack, body, client, command, respond):
    print("Snacc command received")
    # Acknowledge the command request
    ack()

    # Get user ID from the command request
    user_id = body['user_id']

    # Get the profile picture of the user
    user_info = client.users_info(user=user_id)
    user_picture = user_info['user']['profile']['image_192'] 

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You're a snack, <@{user_id}>! :smiling_face_with_smiling_eyes_and_hand_covering_mouth:"
            }
        },
        {
            "type": "image",
            "image_url": user_picture,
            "alt_text": "A Snacc"
        },
    ]

    respond(
        text="You're a snack! :smiling_face_with_smiling_eyes_and_hand_covering_mouth:", 
        blocks = blocks
        )
    
@app.command("/snack")
def snack_command(ack, body, client, command, respond):
    # Acknowledge the command request
    ack()

    credits = get_user_credits(body['user_id'])

    if credits > 0:
        send_unlock_message(body['user_id'], client)
    else:
        respond(
            text="You have 0 credits. Clean for 5 minutes, then send a photo to @<U05T96UN4NN> to earn a credit. See <https://ssi-wiki.stanford.edu/Snack_Bot|the wiki> for more info."
        )

    # Get user ID from the command request
    user_id = body['user_id']

def send_unlock_message(user_id, client):
    credits = get_user_credits(user_id)
    try:
        # Construct the message payload
        message_payload = {
            "channel": user_id,
            "text": "Choose an option",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Thank you for cleaning! You now have {credits} credits. What would you like to do?"}
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Unlock Cabinet 1"},
                            "action_id": "unlock_1"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Unlock Cabinet 2"},
                            "action_id": "unlock_2"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Unlock Cabinet 3"},
                            "action_id": "unlock_3"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Save Credit"},
                            "action_id": "save_credit"
                        }
                    ]
                }
            ]
        }

        # Send the message
        response = client.chat_postMessage(
            channel=user_id,
            blocks=message_payload['blocks'],
            text=message_payload['text']
        )
        return response['ts']
    except Exception as e:
        print(f"Error sending unlock message: {e}")


def download_file(file_url, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download file: ", response.status_code)
        return None 


@app.event("file_shared")
def handle_file_upload(event, client, logger):
    user_id = event['user_id']  # User ID of the user who uploaded the file
    file_id = event['file_id']  # File ID of the uploaded file
    channel_id = event['channel_id']  # Channel ID where the file was uploaded
    snackbot_pics_channel_id = "C06BLHGG5GX"

    file_data = client.files_info(file=file_id)
    file_url = file_data['file']['url_private_download']

    # Download the file
    file = download_file(file_url, os.environ.get('SLACK_BOT_TOKEN'))

    #Posts a message to the channel
    client.chat_postMessage(
        channel=snackbot_pics_channel_id,
        text="@<user_id> earned a credit!"
    )

    #post the file to the channel
    response = client.files_upload(
        channels=snackbot_pics_channel_id,
        file=file,
        initial_comment="A snack!"
    )

    #reacts to the file
    client.reactions_add(channel = snackbot_pics_channel_id, name = "not-clean", timestamp = response['file']['shares']['public'][snackbot_pics_channel_id][0]['ts'])



    if channel_id.startswith('D'):  # Check if the file is uploaded in a DM
        # Logic to handle the file upload
        try:
            # Additional code to process the file
            send_unlock_message(channel_id, client)
        except Exception as e:
            print(f"Error processing uploaded file: {e}")

    update_user_credits(event['user_id'], 1)

@app.action("unlock_1")
def handle_unlock_1(ack, body, client, logger):
    ack()
    try:
        channel_id = body['channel']['id']
        message_ts = body['container']['message_ts']
        client.chat_delete(channel=channel_id, ts=message_ts)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

    asyncio.create_task(actuate_solenoid(1))   

    update_user_credits(body['user']['id'], -1)  

    # Send a follow-up message
    client.chat_postMessage(
        channel=channel_id,
        text="Drawer 1 has been unlocked."
    )        

@app.action("unlock_2")
def handle_unlock_2(ack, body, logger):
    ack()
    # Implement the logic for "Unlock 2"
    logger.info("Unlock 2 was clicked")

@app.action("unlock_3")
def handle_unlock_3(ack, body, logger):
    ack()
    # Implement the logic for "Unlock 3"
    logger.info("Unlock 3 was clicked")

@app.action("save_credit")
def handle_save_credit(ack, body, client, logger):
    ack()
    # Implement the logic for "Save Credit"
    logger.info("Save Credit was clicked")        

    credits = get_user_credits(body['user']['id'])
    if credits == 1:
        msg = "credit"
    else:
        msg = "credits"

    client.chat_postMessage(
        channel=channel_id,
        text=f"Credit has been saved. You now have {credits} {msg}. You can use it later with `/snack`."
    )   
    

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
