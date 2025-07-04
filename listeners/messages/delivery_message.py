from logging import Logger

from slack_bolt import BoltContext, Say

def delivery_message_callback(context: BoltContext, say: Say, logger: Logger):
    try:
        delivery_id = context["matches"][0]
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Delivery *{delivery_id}* has been submitted. Is this correct?"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Correct",
                                "emoji": True
                            },
                            "style": "primary",
                            "action_id": "approve_delivery"
                        },
                        {
                            "type": "button", 
                            "text": {
                                "type": "plain_text",
                                "text": "Not correct",
                                "emoji": True
                            },
                            "style": "danger",
                            "action_id": "deny_delivery"
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        logger.error(e)
