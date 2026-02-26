import os


def welcome_message():
    return f"Welcome!"

def health_status():
    return {"status": "healthy"}

def greetings():
    return "I'm good, how about you?"

def get_version():
    return os.environ.get("APP_VERSION")
