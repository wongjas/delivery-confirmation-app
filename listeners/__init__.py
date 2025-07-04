from listeners import messages
from listeners import actions
from listeners import views

def register_listeners(app):
    messages.register(app)
    actions.register(app)
    views.register(app)