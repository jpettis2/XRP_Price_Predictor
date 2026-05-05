import requests
import json
import csv 
from datetime import datetime
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Class XRPMarketTracker
class XRPMarketTracker():
    def __init__(self, filename="xrp_market_data.csv"):
        self.filename = filename
        self.snapshot_count = 0

        # Activates interactive plotting
        plt.ion()

    # == Function Definition: get_market_snapshot() ==
    # The function sends a POST payload to livecoinwatch.com to receive a json containing metadata of XRP

    # Request provided by LiveCoinWatch
    def get_market_snapshot(self):

        url = "https://api.livecoinwatch.com/coins/single"

        payload = json.dumps({
        "currency": "USD",
        "code": "XRP",
        "meta": True
        })

        headers = {
        'content-type': 'application/json',
        'x-api-key': '55bb6fca-4cb7-4eb5-b3f9-013f8521a9b6'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Display json (will display once if correctly called)
        if self.snapshot_count < 1:
            print(response.text)    
        # Update counter
        self.snapshot_count += 1

        data = response.json()

        print("\nExtracting details from json...")

        # Price Display
        print("\n=== Current Conditions ===\n")
        print(f"Snapshot #: {self.snapshot_count}")
        print(f"Current Date-Time: {datetime.now()}\n")
        print(f"Price: ${data['rate']:.4f}")
        print(f"Volume: {data['volume']/1000000:.3f}M")
        print(f"Market Cap: ${data['cap']/1000000000:.1f}B")
        print(f"Liquidity: {data['liquidity']}")

        # Deltas (Daily, Weekly, Monthly)
        daily_change = (data['delta']['day'] - 1) * 100
        weekly_change = (data['delta']['week'] - 1) * 100
        monthly_change = (data['delta']['month'] - 1) * 100

        # Display Price Change
        print("\n=== Price Changes ===\n")

        print(f"Daily: {daily_change:+.2f}%")
        print(f"Weekly: {weekly_change:+.2f}%")
        print(f"Monthly: {monthly_change:+.2f}%")

        # Check if CSV exists
        file_exists = os.path.isfile(self.filename)

        # Appends data to .csv file. Creates file if it does not exist
        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)

            if self.snapshot_count <= 1:
                print("\n== Checking for .csv file ==\n")

            if not file_exists:
                print(f"Creating .csv file named: {self.filename}\n")

                writer.writerow([
                    "timestamp",
                    "price",
                    "volume",
                    "market_cap",
                    "daily_change",
                    "weekly_change",
                    "monthly_change"
                ])

            writer.writerow([
                datetime.now(),
                data["rate"],
                data["volume"],
                data["cap"],
                daily_change,
                weekly_change,
                monthly_change
            ])

        # CSV Save Notification
        print("\n== Exporting to csv file ==\n")
        print(f"Data saved to {self.filename}...\nWaiting 5 seconds to receive & append additional data...\n")

    # Read .csv file
    def read_data(self):
        df = pd.read_csv(self.filename)
        return df

    # Plot data from .csv file
    def plot_data(self):
        df = pd.read_csv(self.filename)

        if len(df) < 2:
            print("Not enough data to plot yet.")
            return

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        plt.clf()

        plt.plot(df["timestamp"], df["price"], marker="o", label="Actual Price")

        if len(df) >= 5:
            recent = df

            x = np.arange(len(recent))
            y = recent["price"].values

            slope, intercept = np.polyfit(x, y, 1)

            next_x = len(recent)
            predicted_price = slope * next_x + intercept

            next_time = df["timestamp"].iloc[-1] + pd.Timedelta(minutes=1)

            plt.scatter(next_time, predicted_price, marker="x", s=100, label="Predicted Next Price")

            print(f"Predicted next price: ${predicted_price:.4f}")

        plt.title("Live XRP Price")
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.pause(0.1)

    # Periodically obtain market data
    def run(self):
        while True:
            self.get_market_snapshot()
            self.plot_data()
            time.sleep(5)   

def main():
    tracker = XRPMarketTracker()
    tracker.run()

if __name__ == "__main__":
    main()
