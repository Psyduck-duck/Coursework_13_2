import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from data.__init__ import PATH_TO_DATA_DIRECTORY

load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")


def get_alphavantage_data(filename: str) -> None:
    """Записывает в файл json в дирректтории data информацию об интересующих акциях"""

    path_to_file = os.path.join(PATH_TO_DATA_DIRECTORY, filename)
    stocks_dict = {}

    with open("../user_settings.json") as file:
        data = json.load(file)
        user_stocks = data.get("user_stocks")
        user_currencies = data.get("user_currencies")

    for x in user_currencies:

        headers = {"apikey": apilayer_API_KEY}
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={x}&amount=1"
        responce = requests.get(url, headers=headers)
        if responce.status_code != 200:
            raise ValueError("Check URL")
        data = responce.json()

        stocks_dict[x] = f"{round(data.get("result"), 2)} RUB"

    for i in user_stocks:

        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={i}&interval=5min&apikey={API_KEY_alphavantage}"
        responce = requests.get(url)
        if responce.status_code != 200:
            raise ValueError("Check URL")
        data = responce.json()
        stocks_dict[i] = data

    with open(path_to_file, "w", encoding="utf-8") as f:
        json.dump(stocks_dict, f, ensure_ascii=False, indent=4)


def get_greeting(date: datetime) -> str:
    """Фукнция возвращмет приветствие в зависимости от времени суток"""
    hour = date.hour
    if hour < 4:
        return "Доброй ночи"
    elif hour < 10:
        return "Доброе утро"
    elif hour < 16:
        return "Добрый день"
    elif hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_operations_data(path_to_file: str):
    """Возвращает датафрейм с данными"""

    try:
        df = pd.read_excel(path_to_file)
    except:
        raise Exception("file not found")
    return df


def get_card_info(df, date_stop: datetime) -> list[dict]:
    """Возвращает информацию по каждой карте"""

    month = date_stop.month
    year = date_stop.year
    date_start = datetime.datetime(year, month, 1)
    sorted_df = df.loc[df["Номер карты"].notnull()]
    sorted_df["Дата операции"] = pd.to_datetime(sorted_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    sorted_df = sorted_df[(sorted_df["Дата операции"] >= date_start) & (sorted_df["Дата операции"] <= date_stop)]
    cards_info = []
    cards_uniq_numbers = sorted_df["Номер карты"].unique()

    for card in cards_uniq_numbers:
        card_mask = card[-4:]
        spending_operations = sorted_df.loc[(sorted_df["Номер карты"] == card) & (sorted_df["Сумма платежа"] < 0)]
        total_spending = spending_operations["Сумма платежа"].sum()
        cards_info.append({
      "last_digits": card_mask,
      "total_spent": round(float(total_spending), 2) * -1,
      "cashback": round((float(total_spending) / 100), 2) * -1
    })

    return cards_info





#######################################################################################################

#get_alphavantage_data("user_financial_info.json")

# with open("../user_settings.json") as file:
# data = json.load(file)
# print(data.get("user_stocks"))

#print(get_greeting())

df = get_operations_data("../data/operations.xlsx")
date_obj = datetime.datetime(2020, 1, 12)
#df = df.loc[df["Сумма платежа"] < 0]
#print(df["Номер карты"].unique())

#print(df["Сумма платежа"].sum())

print(get_card_info(df, date_obj))