import requests
import os
from datetime import datetime, timedelta

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
STOCK_API_KEY = os.environ["STOCK_API_KEY"]

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NEWS_ALERT_THRESHHOLD = 0.02

# Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
params_stock_api = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

response = requests.get(f"https://www.alphavantage.co/query", params=params_stock_api)
response.raise_for_status()
time_series_data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in time_series_data.items()]

# Get yesterday and day before yesterday's closing prices
yesterday_close = float(data_list[-1]["4. close"])
day_before_yesterday_close = float(data_list[-1]["4. close"])


# Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
def get_news():
    yesterday = datetime.today() - timedelta(1)
    params_news_api = {
        "q": COMPANY_NAME,
        "to": str(yesterday.date()),
        "from": str(yesterday.date()),
        "sortBy": "popularity",
        "apikey": NEWS_API_KEY
    }
    news_request = requests.get("https://newsapi.org/v2/everything", params=params_news_api)
    news_request.raise_for_status()
    news = news_request.json()["articles"][:3]
    return news


if abs(yesterday_close - day_before_yesterday_close) / day_before_yesterday_close > NEWS_ALERT_THRESHHOLD:
    news = get_news()

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

