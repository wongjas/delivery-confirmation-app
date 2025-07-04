from slack_bolt import App
from .approve_deny_buttons import deny_delivery_callback
from .approve_deny_buttons import approve_delivery_callback

def register(app: App):
    app.action("approve_delivery")(approve_delivery_callback)
    app.action("deny_delivery")(deny_delivery_callback)
