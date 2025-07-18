from logging import Logger


def approve_delivery_callback(ack, body, client, logger: Logger):
    try:
        ack()

        delivery_id = body["message"]["text"].split("*")[1]
        # Update the original message so you can't press it twice
        client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Processed delivery *{delivery_id}*...",
                    },
                }
            ],
        )

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "approve_delivery_view",
                "title": {"type": "plain_text", "text": "Approve Delivery"},
                "private_metadata": f"{delivery_id}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Approving delivery *{delivery_id}*",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "notes",
                        "label": {
                            "type": "plain_text",
                            "text": "Additional delivery notes",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "notes_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Add notes...",
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "location",
                        "label": {
                            "type": "plain_text",
                            "text": "Delivery Location",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "location_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": ("Enter the location details..."),
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "channel",
                        "label": {
                            "type": "plain_text",
                            "text": "Notification Channel",
                        },
                        "element": {
                            "type": "channels_select",
                            "action_id": "channel_select",
                            "initial_channel": body["container"]["channel_id"],
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select channel for notifications",
                            },
                        },
                        "optional": False,
                    },
                ],
                "submit": {"type": "plain_text", "text": "Approve"},
            },
        )

        logger.info(f"Approval modal opened by user {body['user']['id']}")
    except Exception as e:
        logger.error(e)


def deny_delivery_callback(ack, body, client, logger: Logger):
    try:
        ack()

        delivery_id = body["message"]["text"].split("*")[1]
        # Update the original message so you can't press it twice.
        client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Delivery *{delivery_id}* was incorrect ❌",
                    },
                }
            ],
        )

        logger.info(f"Delivery denied by user {body['user']['id']}")
    except Exception as e:
        logger.error(e)
