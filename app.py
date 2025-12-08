import json
import requests
import os
from datetime import datetime

URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
LAST_MESSAGE_FILE = 'last_message.json'

PO_URL = "https://api.pushover.net/1/messages.json"
PO_USER = os.environ.get("PO_USER_KEY") # retrieve or None
PO_APP = os.environ.get("PO_APP_KEY") # retrieve or None

# Get the last message to compare, this prevents spamming to the pushover over.
def load_last_message():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as f:
            return json.load(f)
    return None

# Saves the last message to prevent spamming myself; this will also reset daily, by checking the timestamp
def save_last_message(message):
    entry = {
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    with open(LAST_MESSAGE_FILE, 'w') as f:
        json.dump(entry, f)

# Check if last message is from today.
def is_message_from_today(last_message):
    if not last_message or "timestamp" not in last_message:
        return False
    try:
        ts = datetime.fromisoformat(last_message["timestamp"])
        return ts.date() == datetime.now().date()
    except Exception:
        return False

# Get the kp index from the Space Weather Prediction Center
def fetch_kp_data():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status() # raise error if bad status
        data = response.json()
        return data
    except requests.RequestException as e:
        print("Error fetching Kp data:", e)
        return None
    
def get_latest_kp():
    data = fetch_kp_data()
    if not data or len(data) == 0:
        return None
    latest = data[-1]
    kp = float(latest["kp_index"])
    ts = latest["time_tag"]
    return kp, ts

# Send a push notification if Kp >= 5 and not a duplicate
def push_notification(kp, last_message):
    if not PO_USER or not PO_APP:
        return None
    
    message = f"Current Kp Value is {kp}."
    if last_message:
        last_text = last_message["message"]
    else:
        last_text = None
    if kp >= 5 and (not is_message_from_today(last_message) or message != last_text):
        data = {"token": PO_APP,
                "user": PO_USER,
                "message": message,
                "title": "Planet Kp Update!"}
        try:
            response = requests.post(PO_URL, data=data)
            response.raise_for_status()
            print("Notification sent:", message)
            save_last_message(message)
        except requests.RequestException as e:
            print("Error sending notification:", e)


if __name__ == "__main__":
    last_message = load_last_message()
    latest = get_latest_kp()
    if latest:
        kp, ts = latest
        push_notification(kp, last_message)
