import os
import dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables
dotenv.load_dotenv()

# Initialize the Bolt app
app = App(
    token=os.environ.get('SLACK_BOT_TOKEN')
)

@app.command("/snacc")
def snacc_command(ack, body, client, command, respond):
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
    
#/snack [number] checks database if there's enough credits for a snack, and if so turns on gpio pin [number]. It then updates the database to reflect the new number of credits.
@app.command("/snack")
def snack_command(ack, body, client, command, respond):
    # Acknowledge the command request
    ack()

    # Get user ID from the command request
    user_id = body['user_id']

    

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
