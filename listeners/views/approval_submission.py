from logging import Logger
import os

def handle_approve_delivery_view(ack, client, view, logger: Logger):
    try:
        ack()
        
        delivery_id = view["private_metadata"]
        delivery_notes = view["state"]["values"]["delivery_notes"]["delivery_notes_input"]["value"]
        delivery_location = view["state"]["values"]["delivery_location"]["delivery_location_input"]["value"]
        delivery_channel = view["state"]["values"]["delivery_channel"]["delivery_channel_select"]["selected_channel"]

        client.chat_postMessage(
            channel=delivery_channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ Delivery *{delivery_id}* has been approved with the following details:"
                    }
                },
                {
                    "type": "section", 
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Delivery Notes:*\n{delivery_notes if delivery_notes else 'No additional notes provided'}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": f"*Delivery Location:* {delivery_location if delivery_location else 'No location specified'}"
                    }
                }
            ]
        )

        # Extract just the numeric portion from delivery_id
        delivery_number = ''.join(filter(str.isdigit, delivery_id))

        # Update Salesforce order object
        try:
            from simple_salesforce import Salesforce

            sf = Salesforce(
                username=os.environ.get('SF_USERNAME'),
                password=os.environ.get('SF_PASSWORD'), 
                security_token=os.environ.get('SF_TOKEN')
            )

            # Assuming delivery_id maps to Salesforce Order number
            order = sf.query(f"SELECT Id FROM Order WHERE OrderNumber = '{delivery_number}'")
            if order['records']:
                order_id = order['records'][0]['Id']
                sf.Order.update(order_id, {
                    'Status': 'Delivered',
                    'Description': delivery_notes,
                    'Shipping_Location__c': delivery_location  
                })
                logger.info(f"Successfully updated Salesforce order for delivery {delivery_id}")
            else:
                logger.warning(f"No Salesforce order found for delivery {delivery_id}")

        except Exception as sf_error:
            logger.error(f"Salesforce update failed for order {delivery_id}: {sf_error}")
            # Continue execution even if Salesforce update fails


    except Exception as e:
        logger.error(f"Error in approve_delivery_view: {e}")