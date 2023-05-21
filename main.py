import requests
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import time
import json
import os

# URL for the API endpoint
url = "https://api-mainnet.magiceden.io/v2/ord/btc/activities"

# Parameters for the API call
# bitcoin-frogs
# naked-frogs
# npc
params = {
    "limit": 40,
    "offset": 0,
    "collectionSymbol": "npc",
    "kind[]": "buying_broadcasted"
}


# Function to calculate the average of a list
def average(lst):
    return sum(lst) / len(lst)


def is_too_different(new_value):
    if len(previousPoints) >= 5:
        threshold = 0.2  # 20% difference threshold
        previous_values = previousPoints[:5]  # Get the last five values
        max_difference = max(previous_values) * threshold  # Calculate the maximum allowed difference
        if abs(new_value - previous_values[-1]) > max_difference:
            return True
    return False


# Initialize a list for storing data
data = []

# Check if data file exists
if os.path.isfile(f"{params['collectionSymbol']}.json"):
    # Load data from file
    with open(f"{params['collectionSymbol']}.json", 'r') as file:
        data = json.load(file)

    # Parse the most recent date
    latest_date = datetime.fromisoformat(max(item['date'] for item in data))
else:
    # If no file exists, set latest_date to now
    latest_date = datetime(1, 1, 1)

breaker = False
previousPoints = []
# Fetch new entries from the API
while not breaker:
    # Get the next page of results
    response = requests.get(url, params=params).json()

    # Extract data from the 'activities' key
    activities = response['activities']

    # If no more results, break the loop
    if not activities:
        break

    for item in activities:
        date_string = item['createdAt']
        # Convert date to datetime object
        date = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')

        # If this date is older than our most recent date, stop fetching
        if date.replace(tzinfo=timezone.utc) <= latest_date.replace(tzinfo=timezone.utc):
            breaker = True
            break

        new_price = item['listedPrice'] / 100000000.0

        # Only add the price if it's not significantly different from the last 5 prices
        if not is_too_different(new_price):  # 0.2 is the tolerance, adjust as needed
            data.append({'date': date.isoformat(), 'price': new_price})
        else:
            print(f"Value too different {date} - {new_price}")
        previousPoints.insert(0, new_price)

    # Print progress
    print(f"Fetched up to offset {params['offset']}...")

    # Sleep to avoid hitting rate limits
    time.sleep(0.2)

    # Increment offset for the next page
    params['offset'] += 40

data = sorted(data, key=lambda x: datetime.fromisoformat(x["date"]))

# Save data to file
with open(f"{params['collectionSymbol']}.json", 'w') as file:
    json.dump(data, file)

# Extract data for plotting
dates = [datetime.fromisoformat(point['date']) for point in data]
prices = [point['price'] for point in data]

# Plot the data
plt.plot(dates, prices)
plt.xlabel('Created At')
plt.ylabel('Listed Price')
plt.title('Listed Price over Time')
plt.show()
