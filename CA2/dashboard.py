import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
import dash
import dash_core_components as dcc
import dash_html_components as html
from sklearn.ensemble import RandomForestRegressor
# Load data from CSV
df = pd.read_csv('preprocessedSD.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Sort the data by date in ascending order
df = df.sort_values('Date')
df['Date'] = pd.to_datetime(df['Date'])

def predict(model, data, w, n):
    """
    Predicts the forecast for the next n days based on the given window size.
    
    Args:
        model: The trained machine learning model.
        data: The input data containing the historical values.
        w: The window size used for training the model.
        n: The number of days to forecast.
        
    Returns:
        The forecasted values for the next n days.
    """
    forecast = []
    num_samples = len(data)
    
    for i in range(num_samples - w, num_samples):
        window = data[i-w:i].reshape(1, -1)
        forecast.append(model.predict(window))
    
    forecast = np.array(forecast).flatten()
    return forecast[-n:]


# Define function for generating forecasts
def generate_forecast(data, window_size, forecast_horizon, model):
    X = []
    y = []
    for i in range(len(data) - window_size - forecast_horizon + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size:i+window_size+1])
    X = np.array(X)
    y = np.array(y)
    model.fit(X, y)
    
    
    return predict(model, data, window_size, forecast_horizon)

# Prepare data for modeling
data = df['Average_Sentiment'].values

# Define models
linear_reg = LinearRegression()
ridge_reg = Ridge()
random_forest_reg = RandomForestRegressor()

# Define window sizes and forecast horizons
window_sizes = [10, 20, 30]
forecast_horizons = [7, 30, 90]

# Train models and generate forecasts
forecasts = []
for window_size in window_sizes:
    window_forecasts = []
    for horizon in forecast_horizons:
        model_forecast = generate_forecast(data, window_size, horizon, linear_reg)
        window_forecasts.append(model_forecast)
    forecasts.append(window_forecasts)

# Calculate metrics (e.g., RMSE)
rmse_scores = []
for window_forecasts in forecasts:
    window_rmse = []
    for forecast in window_forecasts:
        rmse = np.sqrt(mean_squared_error(data[-len(forecast):], forecast.flatten()))
        window_rmse.append(rmse)
    rmse_scores.append(window_rmse)

# Create dashboard using Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('Sentiment Analysis Forecast Dashboard'),
    html.Div(children=[
        html.H2('Forecasts'),
        dcc.Graph(
            id='forecast-graph',
            figure={
                'data': [
                    {'x': forecast_horizons, 'y': forecasts[i], 'type': 'line', 'name': f'Window Size: {window_sizes[i]}'}
                    for i in range(len(forecasts))
                ],
                'layout': {
                    'title': 'Sentiment Analysis Forecasts',
                    'xaxis': {'title': 'Forecast Horizon'},
                    'yaxis': {'title': 'Forecast Value'}
                }
            }
        )
    ]),
    html.Div(children=[
        html.H2('RMSE Scores'),
        dcc.Graph(
            id='rmse-graph',
            figure={
                'data': [
                    {'x': forecast_horizons, 'y': rmse_scores[i], 'type': 'bar', 'name': f'Window Size: {window_sizes[i]}'}
                    for i in range(len(rmse_scores))
                ],
                'layout': {
                    'title': 'RMSE Scores',
                    'xaxis': {'title': 'Forecast Horizon'},
                    'yaxis': {'title': 'RMSE'}
                }
            }
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
