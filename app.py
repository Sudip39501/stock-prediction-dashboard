from flask import Flask, render_template, jsonify, request
import logging
from datetime import datetime, timedelta
from config import STOCKS
from data_fetcher import get_stock_data, get_historical_data
from model_predictor import create_lstm_model, prepare_training_data, make_predictions, predict_future_prices
import requests
import numpy as np

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stocks')
def get_stocks():
    stocks_data = []
    
    for stock in STOCKS:
        try:
            stock_data = get_stock_data(stock["symbol"])
            
            if stock_data:
                stocks_data.append({
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "price": stock_data["price"],
                    "avg_daily_return": stock_data["avg_return"]
                })
            else:
                logger.warning(f"No data for {stock['symbol']}, skipping")
                continue
                
        except Exception as e:
            logger.error(f"Unexpected error for {stock['symbol']}: {str(e)}")
            continue
    
    logger.info(f"Returning {len(stocks_data)} stocks")
    return jsonify(stocks_data)

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    return render_template('stock.html', symbol=symbol)

@app.route('/stock/<symbol>/history')
def get_stock_history(symbol):
    try:
        hist_3m = get_historical_data(symbol, '3m')
        hist_6m = get_historical_data(symbol, '6m')
        hist_1y = get_historical_data(symbol, '1y')
        
        if not hist_3m or not hist_6m or not hist_1y:
            return jsonify({"error": "Could not fetch historical data"}), 500
        
        return jsonify({
            "3m": hist_3m,
            "6m": hist_6m,
            "1y": hist_1y
        })
        
    except Exception as e:
        logger.error(f"Error in history endpoint for {symbol}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/stock/<symbol>/predict', methods=['POST'])
def predict_stock(symbol):
    try:
        # Get 2 years of historical data for training
        from config import YAHOO_FINANCE_URL, REQUEST_HEADERS, REQUEST_TIMEOUT
        
        url = f"{YAHOO_FINANCE_URL}/{symbol}"
        params = {
            'range': '2y',
            'interval': '1d'
        }
        
        response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            return jsonify({"error": "No data available for prediction"}), 400
        
        result = data['chart']['result'][0]
        quotes = result['indicators']['quote'][0]
        
        # Prepare data for LSTM
        closes = [close for close in quotes['close'] if close is not None]
        
        if len(closes) < 60:
            return jsonify({"error": "Not enough historical data for prediction"}), 400
        
        # Prepare training data
        x_train, y_train, training_data_len, scaled_data, scaler = prepare_training_data(closes)
        
        # Build and train LSTM model
        model = create_lstm_model((x_train.shape[1], 1))
        model.fit(x_train, y_train, batch_size=1, epochs=1, verbose=0)
        
        # Make predictions
        predictions = make_predictions(model, scaled_data, training_data_len, scaler)
        
        # Get actual values for comparison
        data_array = np.array(closes).reshape(-1, 1)
        actual = data_array[training_data_len:]
        
        # Predict future prices
        future_predictions = predict_future_prices(model, scaled_data, scaler)
        
        # Format results
        actual_prices = [float(price) for price in actual.flatten()]
        predicted_prices = [float(price) for price in predictions.flatten()]
        future_dates = [
            (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') 
            for i in range(30)
        ]
        future_prices = [float(price) for price in future_predictions.flatten()]
        
        return jsonify({
            "actual": actual_prices,
            "predicted": predicted_prices,
            "future_dates": future_dates,
            "future_prices": future_prices
        })
        
    except Exception as e:
        logger.error(f"Error in prediction for {symbol}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test_api():
    return jsonify({
        "message": "API is working!", 
        "status": "success",
        "timestamp": datetime.now().isoformat()
    
    })


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)