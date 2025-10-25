# Sample stocks to display
STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NFLX", "name": "Netflix Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"}
]

YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
REQUEST_TIMEOUT = 10

# Model configuration
SEQUENCE_LENGTH = 60
PREDICTION_DAYS = 30
TRAINING_SPLIT_RATIO = 0.8