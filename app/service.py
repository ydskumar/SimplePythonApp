
import os


def welcome_message():
    return f"Welcome!"

def health_status():
    if os.environ.get("FAIL_HEALTH") == "true":
        return {"status": "DOWN"}, 500
    return {"status": "UP"}

def greetings():
    return "I'm good, how about you?"