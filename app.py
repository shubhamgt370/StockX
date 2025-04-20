import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from datetime import date
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score

st.title('StockX')
st.sidebar.info("StockX's ML Prediction Model.")

def main():
    option = st.sidebar.selectbox('Make a choice', ['Recent Data', 'Predict'])
    if option == 'Recent Data':
        dataframe()
    else:
        predict()

@st.cache_resource
def download_data(op, start_date, end_date):
    df = yf.download(op, start=start_date, end=end_date, progress=False)
    return df

option = st.sidebar.text_input('Enter a Stock Symbol', value='SPY')
option = option.upper()
today = datetime.date.today()
duration = st.sidebar.number_input('Enter the duration', value=3000)
before = today - datetime.timedelta(days=duration)
start_date = st.sidebar.date_input('Start Date', value=before)
end_date = st.sidebar.date_input('End date', today)

if st.sidebar.button('Send'):
    if start_date < end_date:
        st.sidebar.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
        download_data(option, start_date, end_date)
    else:
        st.sidebar.error('Error: End date must fall after start date')

data = download_data(option, start_date, end_date)
scaler = StandardScaler()

def dataframe():
    st.header('Recent Data')
    st.dataframe(data.tail(10))

def predict():
    model = st.radio('Choose a model', ['LinearRegression', 'RandomForestRegressor', 'ExtraTreesRegressor', 'KNeighborsRegressor', 'XGBoostRegressor'])
    num = st.number_input('How many days forecast?', value=5)
    num = int(num)
    if st.button('Predict'):
        if model == 'LinearRegression':
            engine = LinearRegression()
        elif model == 'RandomForestRegressor':
            engine = RandomForestRegressor()
        elif model == 'ExtraTreesRegressor':
            engine = ExtraTreesRegressor()
        elif model == 'KNeighborsRegressor':
            engine = KNeighborsRegressor()
        else:
            engine = XGBRegressor()
        model_engine(engine, num)

def model_engine(model, num):
    df = data[['Close']]
    df['preds'] = data.Close.shift(-num)
    x = df.drop(['preds'], axis=1).values
    x = scaler.fit_transform(x)
    x_forecast = x[-num:]
    x = x[:-num]
    y = df.preds.values
    y = y[:-num]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=7)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    st.text(f'r2_score: {r2_score(y_test, preds)}')

    forecast_pred = model.predict(x_forecast)
    forecast_pred = forecast_pred[::-1]  # Reverse order

    for day, price in enumerate(forecast_pred, start=1):
        st.text(f'Day {day}: {price}')

if __name__ == '__main__':
    main()