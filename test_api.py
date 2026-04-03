import requests
import os

key = "xxxxxxxxxxxx"
symbol = "AAPL"
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'

print(f"Testing URL for {symbol}...")
try:
    r = requests.get(url)
    data = r.json()
    if "Time Series (Daily)" in data:
        print("SUCCESS: Data found.")
        # print first key to verify
        print("First date:", list(data["Time Series (Daily)"].keys())[0])
    else:
        print("FAILURE: 'Time Series (Daily)' not found.")
        print("Response keys:", data.keys())
        print("Full Response:", data)
except Exception as e:
    print("EXCEPTION:", e)
