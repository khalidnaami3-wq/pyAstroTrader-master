"""
Data fetcher module supporting both AlphaVantage and Yahoo Finance
"""
import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_data_yfinance(ticker, years=20):
    """
    Fetch stock data using Yahoo Finance (free, no API key needed)
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'MSFT')
        years: Number of years of historical data
    
    Returns:
        pandas DataFrame with columns: Date, Price, Open, High, Low, Vol
    """
    print(f"Fetching data for {ticker} using Yahoo Finance...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    
    # Download data
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    
    # Rename columns to match expected format
    df_formatted = pd.DataFrame({
        'Date': df.index.strftime('%Y%m%d'),
        'Price': df['Close'],
        'Open': df['Open'],
        'High': df['High'],
        'Low': df['Low'],
        'Vol': df['Volume']
    })
    
    df_formatted = df_formatted.reset_index(drop=True)
    
    print(f"Successfully fetched {len(df_formatted)} days of data for {ticker}")
    return df_formatted

def fetch_data_alphavantage(ticker, api_key):
    """
    Fetch stock data using AlphaVantage API
    
    Args:
        ticker: Stock symbol
        api_key: AlphaVantage API key
    
    Returns:
        pandas DataFrame with columns: Date, Price, Open, High, Low, Vol
    """
    print(f"Fetching data for {ticker} using AlphaVantage...")
    
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={api_key}'
    
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError('Error in getting the Data from AlphaVantage')
    
    data = response.json()
    
    if 'Time Series (Daily)' not in data:
        raise ValueError(f"Invalid response from AlphaVantage: {data.get('Note', data.get('Error Message', 'Unknown error'))}")
    
    data_to_process = data['Time Series (Daily)']
    days = list(data_to_process.keys())
    
    data_for_pandas = []
    for current_day in days:
        if float(data_to_process[current_day]['4. close']) == 0:
            continue
        
        data_for_pandas.append({
            'Date': current_day.replace('-', ''),
            'Price': float(data_to_process[current_day]['4. close']),
            'Open': float(data_to_process[current_day]['1. open']),
            'High': float(data_to_process[current_day]['2. high']),
            'Low': float(data_to_process[current_day]['3. low']),
            'Vol': float(data_to_process[current_day]['5. volume'])
        })
    
    df = pd.DataFrame(sorted(data_for_pandas, key=lambda x: x['Date'], reverse=False))
    
    print(f"Successfully fetched {len(df)} days of data for {ticker}")
    return df

def fetch_stock_data(ticker, api_key=None, source='auto'):
    """
    Fetch stock data using the best available source
    
    Args:
        ticker: Stock symbol
        api_key: AlphaVantage API key (optional if using yfinance)
        source: 'auto', 'yfinance', or 'alphavantage'
    
    Returns:
        pandas DataFrame with stock data
    """
    if source == 'yfinance':
        return fetch_data_yfinance(ticker)
    elif source == 'alphavantage':
        if not api_key:
            raise ValueError("API key required for AlphaVantage")
        return fetch_data_alphavantage(ticker, api_key)
    else:  # auto
        # Try yfinance first (free, no limits)
        try:
            return fetch_data_yfinance(ticker)
        except Exception as e:
            print(f"YFinance failed: {e}")
            if api_key:
                print("Falling back to AlphaVantage...")
                return fetch_data_alphavantage(ticker, api_key)
            else:
                raise ValueError("YFinance failed and no AlphaVantage API key provided")

if __name__ == '__main__':
    # Test the fetcher
    ticker = os.environ.get('ASSET_TO_CALCULATE', 'AAPL')
    api_key = os.environ.get('ALPHAVANTAGE_KEY')
    
    df = fetch_stock_data(ticker, api_key, source='auto')
    print(df.head())
    print(f"\nTotal records: {len(df)}")
