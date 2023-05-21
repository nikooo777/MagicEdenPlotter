import requests
import matplotlib.pyplot as plt
from datetime import datetime
import time
import json
import os

# URL for the API endpoint
url = "https://api-mainnet.magiceden.io/v2/ord/btc/activities"

# Parameters for the API call
# Parameters for the API call
# bitcoin-frogs
# npc
# naked-frogs
params = {
    "limit": 40,
    "offset": 0,
    "collectionSymbol": "npc",
    "kind[]": "buying_broadcasted"
}

# Lists to store data for the plot
dates = []
prices = []


# Function to calculate the average of a list
def average(lst):
    return sum(lst) / len(lst)


# Check if data file exists
if os.path.isfile(f"{params['collectionSymbol']}.json"):
    # Load data from file
    with open(f"{params['collectionSymbol']}.json", 'r') as file:
        data = json.load(file)
        dates = data['dates']
        prices = data['prices']
else:
    # Get the first page of results
    response = requests.get(url, params=params).json()

    # Extract data from the 'activities' key
    activities = response['activities']

    # Loop through the pages until all results are returned
    while activities:
        # Extract data from the results
        for item in activities:
            date_string = item['createdAt']
            # Convert date to datetime object
            date = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
            new_price = item['listedPrice'] / 100000000.0

            # Only add the price if it's not significantly different from the last 5 prices
            if len(prices) < 5 or abs(new_price - average(prices[-5:])) / average(
                    prices[-5:]) < 0.2:  # 0.2 is the tolerance, adjust as needed
                dates.append(date.isoformat())
                prices.append(new_price)

        # Print progress
        print(f"Fetched up to offset {params['offset']}...")

        # Sleep to avoid hitting rate limits
        time.sleep(0.2)

        # Increment offset for the next page
        params['offset'] += 40

        # Get the next page of results
        response = requests.get(url, params=params).json()

        # Extract data from the 'activities' key
        activities = response['activities']

    # Save data to file
    with open(f"{params['collectionSymbol']}.json", 'w') as file:
        json.dump({'dates': dates, 'prices': prices}, file)

# Convert dates back to datetime objects for plotting
dates = [datetime.fromisoformat(date) for date in dates]

# Plot the data
plt.plot(dates, prices)
plt.xlabel('Created At')
plt.ylabel('Listed Price')
plt.title('Listed Price over Time')
plt.show()
