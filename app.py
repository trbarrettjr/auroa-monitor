import pickle
import requests
import numpy as np
import os

URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
LAST_MESSAGE_FILE = 'last_message.pkl'

PO_URL = "https://api.pushover.net/1/messages.json"
PO_USER = os.environ.get("PO_USER_KEY") # retrieve or None
PO_APP = os.environ.get("PO_APP_KEY") # retrieve or None

# Get the last message to compare, this prevents spamming to the pushover over.
def load_last_message():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'rb') as f:
            return pickle.load(f)
    return None

# Saves the last message to prevent spamming myself.
def save_last_message(message):
    with open(LAST_MESSAGE_FILE, 'wb') as f:
        pickle.dump(message, f)

# Trend detection, I am using linear regression.
# Boy was this a lot of research, only to find out it
# was built into numpy
def check_trend_regression(data):
    if len(data) < 2:
        return "same" # not enough data points
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

# Extract latest Kp value and full series
def get_kp_series():
    data = fetch_kp_data()
    if not data or len(data) == 0:
        return None, None
    
    kp_values = [float(entry["kp_index"]) for entry in data if "kp_index" in entry]
    latest = data[-1]
    latest_kp = float(latest["kp_index"])
    timestamp = latest["time_tag"]
    return kp_values, (latest_kp, timestamp)

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
    last_message = load_last_message()
    kp_series, latest = get_kp_series()

    if kp_series and latest:
        kp, ts = latest
        trend = check_trend_regression(kp_series)
        push_notification(kp, trend, last_message)
