import os
import time


def welcome_message():
    return f"Welcome!"

def health_status():
    return {"status": "healthy"}

def greetings():
    return "I'm good, how about you?"

def get_version():
    return os.environ.get("APP_VERSION")

def get_metrics(start_time):
    return {
        "status": "healthy",
        "uptime": time.time() - start_time
    }