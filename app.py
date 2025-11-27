import pickle
import requests
import numpy as np
import os
from collections import deque

URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
PICKLE_FILE = 'kp_values.pkl'
LAST_MESSAGE_FILE = 'last_message.pkl'

PO_URL = "https://api.pushover.net/1/messages.json"
PO_USER = os.environ.get("PO_USER_KEY") # retrieve or None
PO_APP = os.environ.get("PO_APP_KEY") # retrieve or None

# Saving the kp list as a python pickle file
def load_state():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            data = pickle.load(f)
            return deque(data, maxlen=10)
    return deque(maxlen=10)

def save_state(kp_values):
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(list(kp_values), f)

def load_last_message():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'rb') as f:
            return pickle.load(f)
    return None

def save_last_message(message):
    with open(LAST_MESSAGE_FILE, 'wb') as f:
        pickle.dump(message, f)

# Trend detection, I am using linear regression.
# Boy was this a lot of research, only to find out it
# was built into numpy
def check_trend_regression(data):
    x = np.arange(len(data))
    y = np.array(data)
    slope, _ = np.polyfit(x, y, 1)
    if slope > 0.05:
        return "up"
    elif slope < -0.05:
        return "down"
    else:
        return "same"

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

# Us the previous function to get the data.
def get_latest_kp():
    data = fetch_kp_data()
    if not data:
        return None
    
    # Entry Keys are ["time_tag", "kp_index", "estimated_kp", "kp"]
    latest = data[-1] # last entry in the list
    kp_value = float(latest["kp_index"])
    timestamp = latest["time_tag"]
    return kp_value, timestamp

def push_notification(kp, trend, last_message):
    if not PO_USER or not PO_APP:
        return None
    
    message = f"Current Kp Value is {kp} and is trending {trend}"
    if kp >= 5 and message != last_message:
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
    kp_values = load_state()
    last_message = load_last_message()

    latest = get_latest_kp()
    if latest:
        kp, ts = latest
        kp_values.append(kp)

        if len(kp_values) == 10:
            trend = check_trend_regression(list(kp_values))
            push_notification(kp, trend, last_message)

        save_state(kp_values)
