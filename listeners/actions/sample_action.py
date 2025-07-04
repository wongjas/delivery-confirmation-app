from logging import Logger

from slack_bolt import Ack
from slack_sdk import WebClient


def sample_action_callback(ack: Ack, client: WebClient, body: dict, logger: Logger):
    try:
        ack()
        client.views_update(
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            view={
                "type": "modal",
                "callback_id": "sample_view_id",
                "title": {
                    "type": "plain_text",
                    "text": "Update modal title",
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Nice! You updated the modal! 🎉",
                        },
                    },
                    {
                        "type": "image",
                        "image_url": "https://media.giphy.com/media/SVZGEcYt7brkFUyU90/giphy.gif",
                        "alt_text": "Yay! The modal was updated",
                    },
                    {
                        "type": "input",
                        "block_id": "input_block_id",
                        "label": {
                            "type": "plain_text",
                            "text": "What are your hopes and dreams?",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "sample_input_id",
                            "multiline": True,
                        },
                    },
                    {
                        "block_id": "select_channel_block_id",
                        "type": "input",
                        "label": {
                            "type": "plain_text",
                            "text": "Select a channel to message the result to",
                        },
                        "element": {
                            "type": "conversations_select",
                            "action_id": "sample_dropdown_id",
                            "response_url_enabled": True,
                        },
                    },
                ],
                "submit": {"type": "plain_text", "text": "Submit"},
            },
        )
    except Exception as e:
        logger.error(e)
