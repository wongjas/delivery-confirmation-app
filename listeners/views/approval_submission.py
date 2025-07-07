from logging import Logger
import os


def handle_approve_delivery_view(ack, client, view, logger: Logger):
    try:
        ack()

        delivery_id = view["private_metadata"]
        values = view["state"]["values"]
        notes = values["notes"]["notes_input"]["value"]
        loc = values["location"]["location_input"]["value"]
        channel = values["channel"]["channel_select"]["selected_channel"]

        client.chat_postMessage(
            channel=channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (f"✅ Delivery *{delivery_id}* approved:"),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (f"*Delivery Notes:*\n{notes or 'None'}"),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (f"*Delivery Location:*\n{loc or 'None'}"),
                    },
                },
            ],
        )

        # Extract just the numeric portion from delivery_id
        delivery_number = "".join(filter(str.isdigit, delivery_id))

        # Update Salesforce order object
        try:
            from simple_salesforce import Salesforce

            sf = Salesforce(
                username=os.environ.get("SF_USERNAME"),
                password=os.environ.get("SF_PASSWORD"),
                security_token=os.environ.get("SF_TOKEN"),
            )

            # Assuming delivery_id maps to Salesforce Order number
            order = sf.query(f"SELECT Id FROM Order WHERE OrderNumber = '{delivery_number}'")  # noqa: E501
            if order["records"]:
                order_id = order["records"][0]["Id"]
                sf.Order.update(
                    order_id,
                    {
                        "Status": "Delivered",
                        "Description": notes,
                        "Shipping_Location__c": loc,
                    },
                )
                logger.info(f"Updated order {delivery_id}")
            else:
                logger.warning(f"Noorder found for {delivery_id}")

        except Exception as sf_error:
            logger.error(f"Update failed for order {delivery_id}: {sf_error}")
            # Continue execution even if Salesforce update fails

    except Exception as e:
        logger.error(f"Error in approve_delivery_view: {e}")
