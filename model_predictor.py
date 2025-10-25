import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import logging
from config import SEQUENCE_LENGTH, PREDICTION_DAYS, TRAINING_SPLIT_RATIO

logger = logging.getLogger(__name__)

def create_lstm_model(input_shape):
    """Build LSTM model architecture"""
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def prepare_training_data(closes):
    """Prepare data for LSTM training"""
    if len(closes) < SEQUENCE_LENGTH:
        raise ValueError("Not enough historical data for prediction")
    
    data_array = np.array(closes).reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data_array)
    
    # Create training data
    training_data_len = int(len(scaled_data) * TRAINING_SPLIT_RATIO)
    train_data = scaled_data[0:training_data_len, :]
    
    x_train = []
    y_train = []
    
    for i in range(SEQUENCE_LENGTH, len(train_data)):
        x_train.append(train_data[i-SEQUENCE_LENGTH:i, 0])
        y_train.append(train_data[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    return x_train, y_train, training_data_len, scaled_data, scaler

def make_predictions(model, scaled_data, training_data_len, scaler):
    """Make predictions using trained model"""
    # Create test data
    test_data = scaled_data[training_data_len - SEQUENCE_LENGTH:, :]
    x_test = []
    
    for i in range(SEQUENCE_LENGTH, len(test_data)):
        x_test.append(test_data[i-SEQUENCE_LENGTH:i, 0])
    
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    # Make predictions
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)
    
    return predictions

def predict_future_prices(model, scaled_data, scaler):
    """Predict future stock prices"""
    last_sequence = scaled_data[-SEQUENCE_LENGTH:]
    future_predictions = []
    
    for _ in range(PREDICTION_DAYS):
        x_future = np.array([last_sequence])
        x_future = np.reshape(x_future, (x_future.shape[0], x_future.shape[1], 1))
        
        next_price = model.predict(x_future, verbose=0)
        future_predictions.append(next_price[0, 0])
        
        # Update sequence for next prediction
        last_sequence = np.append(last_sequence[1:], next_price)
    
    future_predictions = scaler.inverse_transform(
        np.array(future_predictions).reshape(-1, 1)
    )
    
    return future_predictions