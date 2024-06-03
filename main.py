import requests
import os
from datetime import datetime, timedelta
from twilio.rest import Client
from typing import Tuple, Dict, List

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
STOCK_API_KEY = os.environ["STOCK_API_KEY"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
MY_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NEWS_ALERT_THRESHHOLD = 5 # percentage move over which an alert sms is sent

NEWS_RESPONSE_TYPE = List[Dict[str, str]]


def calculate_price_move(yesterday_close: float, day_before_yesterday_close: float) -> float:
    return round(abs(yesterday_close - day_before_yesterday_close) / day_before_yesterday_close * 100, 2)


def get_close_prices() -> Tuple[float, float]:
    """
    Use https://www.alphavantage.co
    return: closing prices from previous trading day and the day before
    """
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
    return yesterday_close, day_before_yesterday_close


def get_news() -> NEWS_RESPONSE_TYPE:
    """
    # Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    :return: a news list from above api
    """
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


def format_message_body(news_list: NEWS_RESPONSE_TYPE) -> str:
    """
    TSLA: 🔺2%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
    or
    "TSLA: 🔻5%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
    """
    up_or_down = '🔺' if price_move > 0 else '🔻'
    message_body = f"{STOCK}: {up_or_down}{price_move}% \n"
    for i, article in enumerate(news_list):
        message_body = message_body + f"{i+1}. Headline: {article['title']}\n"
        message_body = message_body + f"Brief: {article['description']}\n"

    return message_body


def send_sms_alert(news_list: NEWS_RESPONSE_TYPE) -> None:
    """
    Use https://www.twilio.com
    Send a seperate message with the percentage change and each article's title and description to your phone number.
    """
    message_body = format_message_body(news_list=news_list)
    message = client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        to=MY_PHONE_NUMBER,
        body=message_body
    )

    print(message.sid)


price_move = calculate_price_move(*get_close_prices())

if price_move > NEWS_ALERT_THRESHHOLD:
    news = get_news()
    send_sms_alert(news_list=news)

