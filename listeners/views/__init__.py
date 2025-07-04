from slack_bolt import App
from .approval_submission import handle_approve_delivery_view

def register(app: App):
    app.view("approve_delivery_view")(handle_approve_delivery_view)