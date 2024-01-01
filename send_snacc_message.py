def send_snacc_message(user_id, user_image, client):

    # Send the message
    response = client.chat_postMessage(
        channel=user_id,
        text="You're a snack! :smiling_face_with_smiling_eyes_and_hand_covering_mouth:",
            blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You're a snack, <@{user_id}>! :smiling_face_with_smiling_eyes_and_hand_covering_mouth:"
                }
            },
            {
                "type": "image",
                "image_url": f"{user_image}",
                "alt_text": "A Snacc"
            }
        ])
    
    return response['ts']