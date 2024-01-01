def send_unlock_ephemeral(user_id, credits, client, respond, preface = "", ): #used if invoked from a slash command
    credits_plural = "credits" if credits > 1 else "credit"
    try:
        # Send the message
        respond(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{preface} You have {credits} {credits_plural}. What would you like to do?"}
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
                            "text": {"type": "plain_text", "text": "Save for later"},
                            "action_id": "save_credit"
                        }
                    ]
                }
            ],
            text="Unlock Snack Cabinet"
        )
    except Exception as e:
        print(f"Error sending unlock message: {e}")

def send_unlock_message(user_id, credits, client, preface = ""): #used if invoked from sending photo
    credits_plural = "credits" if credits > 1 else "credit"
    try:
        client.chat_postMessage(
            channel=user_id,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{preface} You have {credits} {credits_plural}. What would you like to do?"}
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
                            "text": {"type": "plain_text", "text": "Save for later"},
                            "action_id": "save_credit"
                        }
                    ]
                }
            ],
            text="Unlock Snack Cabinet"
        )
    except Exception as e:
        print(f"Error sending unlock message: {e}")        