import requests
import logging
from datetime import datetime
from config import YAHOO_FINANCE_URL, REQUEST_HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def get_stock_data(symbol):
    """Get stock data from Yahoo Finance API"""
    try:
        url = f"{YAHOO_FINANCE_URL}/{symbol}"
        params = {
            'range': '1mo',
            'interval': '1d'
        }
        
        response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            raise ValueError("No data returned from API")
        
        result = data['chart']['result'][0]
        
        if 'indicators' not in result or 'quote' not in result['indicators']:
            raise ValueError("No quote data available")
        
        quotes = result['indicators']['quote'][0]
        timestamps = result['timestamp']
        
        # Get closing prices
        closes = quotes['close']
        
        # Filter out None values
        valid_data = [(ts, close) for ts, close in zip(timestamps, closes) if close is not None]
        
        if len(valid_data) < 2:
            raise ValueError("Not enough valid data points")
        
        timestamps, closes = zip(*valid_data)
        
        current_price = closes[-1]
        prev_price = closes[0]
        avg_daily_return = ((current_price - prev_price) / prev_price) * 100
        
        return {
            "price": round(current_price, 2),
            "avg_return": round(avg_daily_return, 2),
            "closes": list(closes),
            "timestamps": list(timestamps)
        }
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_historical_data(symbol, period):
    try:
        # Map periods to Yahoo Finance ranges
        range_map = {
            '3m': '3mo',
            '6m': '6mo',
            '1y': '1y'
        }
        
        url = f"{YAHOO_FINANCE_URL}/{symbol}"
        params = {
            'range': range_map[period],
            'interval': '1d'
        }
        
        response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            raise ValueError("No data returned from API")
        
        result = data['chart']['result'][0]
        quotes = result['indicators']['quote'][0]
        timestamps = result['timestamp']
        
        # Create historical data
        historical_data = []
        for ts, close in zip(timestamps, quotes['close']):
            if close is not None:
                date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                historical_data.append({
                    "date": date,
                    "price": round(close, 2)
                })
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None