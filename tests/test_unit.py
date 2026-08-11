from app.service import welcome_message, greetings

def test_welcome_message():
    assert welcome_message() == "Welcome!"

def test_greeting():
    assert "good" in greetings()