
import os


def welcome_message():
    return f"Welcome!"

def health_status():
    print("FAIL_HEALTH =", os.environ.get("FAIL_HEALTH"))
    if os.environ.get("FAIL_HEALTH") == "true":
        return {"status": "DOWN"}, 500
    return {"status": "healthy"}

def greetings():
    return "I'm good, how about you?"