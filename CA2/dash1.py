import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import dash
import dash_core_components as dcc
import dash_html_components as html

# Load data from CSV file
data = pd.read_csv('preprocessedSD.csv')
dates = pd.to_datetime(data['Date'])
sentiment_scores = data['Average_Sentiment'].values

def generate_forecast(model, window_size, forecast_days):
    # Generate forecast for the next n days
    forecast = []
    last_window = sentiment_scores[-window_size:]
    for _ in range(forecast_days):
        prediction = model.predict([last_window])[0]
        forecast.append(prediction)
        last_window = np.append(last_window[1:], prediction)

    return forecast

# Train models with different window sizes
window_sizes = [10, 20, 30]
models = [LinearRegression(), DecisionTreeRegressor(), RandomForestRegressor()]
from dash.dependencies import Input, Output
forecasts = []
for window_size in window_sizes:
    window_forecasts = []
    X = []
    y = []
    for i in range(len(sentiment_scores) - window_size):
        X.append(list(sentiment_scores[i:i+window_size]))
        y.append(sentiment_scores[i+window_size])
    X = np.array(X)
    y = np.array(y)
    print('Conv for win', str(window_size))
    for model in models:
        model.fit(X,y)
        
        # Generate forecasts for different time periods
        forecast_7_days = generate_forecast(model, window_size, 7)
        forecast_30_days = generate_forecast(model, window_size, 30)
        forecast_90_days = generate_forecast(model, window_size, 90)
        
        window_forecasts.append({
            'model': model.__class__.__name__,
            'window_size': window_size,
            'forecast_7_days': forecast_7_days,
            'forecast_30_days': forecast_30_days,
            'forecast_90_days': forecast_90_days
        })
    forecasts.append(window_forecasts)

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(
    children=[
        html.H1("Forecast Results"),
        dcc.Dropdown(
            id="window-size-dropdown",
            options=[
                {"label": "10 Days", "value": 10},
                {"label": "20 Days", "value": 20},
                {"label": "30 Days", "value": 30}
            ],
            value=10  # Set the default window size
        ),
        dcc.Dropdown(
            id="model-dropdown",
            options=[
                {"label": "LinearRegression", "value": 'LinearRegression'},
                {"label": "DecisionTreeRegressor", "value": 'DecisionTreeRegressor'},
                {"label": "RandomForestRegressor", "value": 'RandomForestRegressor'}
            ],
            value='LinearRegression' 
        ),
        dcc.Graph(id='forecast-chart-7days'),
        dcc.Graph(id='forecast-chart-30days'),
        dcc.Graph(id='forecast-chart-90days')

    ]
)

# Define the callback function to update the chart based on the selected window size
@app.callback(
    [Output('forecast-chart-7days', 'figure'),
     Output('forecast-chart-30days', 'figure'),
     Output('forecast-chart-90days', 'figure')],
    [Input('window-size-dropdown', 'value'),
     Input('model-dropdown', 'value')
     ]
)
def update_chart(window_size, model):
    # Based on the selected window size, choose the corresponding forecast data
    import plotly.graph_objects as go
    for window_forecasts in forecasts:
        for forecast in window_forecasts:
            if forecast['window_size'] == window_size and forecast['model'] == model:
                forecast_data = forecast

    # Create traces for each line
    trace_7days = go.Scatter(
        x=list(range(len(forecast_data['forecast_7_days']))),
        y=forecast_data['forecast_7_days'],
        mode='lines',
        name='7 Days Forecast'
    )
    trace_30days = go.Scatter(
        x=list(range(len(forecast_data['forecast_30_days']))),
        y=forecast_data['forecast_30_days'],
        mode='lines',
        name='30 Days Forecast'
    )
    trace_90days = go.Scatter(
        x=list(range(len(forecast_data['forecast_90_days']))),
        y=forecast_data['forecast_90_days'],
        mode='lines',
        name='90 Days Forecast'
    )   
              
     # Combine traces into data list
    layout_7days = go.Layout(
        title='Forecast for 7 Days',
        xaxis=dict(title='Day'),
        yaxis=dict(title='Forecast Value')
    )
    layout_30days = go.Layout(
        title='Forecast for 30 Days',
        xaxis=dict(title='Day'),
        yaxis=dict(title='Forecast Value')
    )
    layout_90days = go.Layout(
        title='Forecast for 90 Days',
        xaxis=dict(title='Day'),
        yaxis=dict(title='Forecast Value')
    )


    figure_7days = go.Figure(data=[trace_7days], layout=layout_7days)
    figure_30days = go.Figure(data=[trace_30days], layout=layout_30days)
    figure_90days = go.Figure(data=[trace_90days], layout=layout_90days)

    return figure_7days, figure_30days, figure_90days


def update_forecast_output(window_size):
    forecasts_html = []
    
    for window_forecasts in forecasts:
        for forecast in window_forecasts:
            if forecast['window_size'] == window_size:
                forecasts_html.append(html.Div(children=[
                    html.H3(children=forecast['model']),
                    html.H5(children='Window Size: {}'.format(forecast['window_size'])),
                    html.H5(children='Forecast for 7 days: {}'.format(forecast['forecast_7_days'])),
                    html.H5(children='Forecast for 30 days: {}'.format(forecast['forecast_30_days'])),
                    html.H5(children='Forecast for 90 days: {}'.format(forecast['forecast_90_days']))
                ]))
    
    return forecasts_html

if __name__ == '__main__':
    app.run_server(debug=True)
