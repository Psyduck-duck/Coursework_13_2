import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

pd.options.mode.chained_assignment = None

from data.__init__ import PATH_TO_DATA_DIRECTORY

load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")

relative_path_user_setting = "../user_settings.json"
absolute_path_user_settings = os.path.abspath(relative_path_user_setting)


def get_alphavantage_data(filename: str) -> None:
    """Записывает в файл json в дирректтории data информацию об интересующих акциях"""

    path_to_file = os.path.join(PATH_TO_DATA_DIRECTORY, filename)
    stocks_dict = {}

    with open(absolute_path_user_settings) as file:
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


def get_operations_data(filename: str) -> pd.DataFrame:
    """Возвращает датафрейм с данными из директории data"""

    path_to_file = os.path.join(PATH_TO_DATA_DIRECTORY, filename)

    try:
        df = pd.read_excel(path_to_file)
    except:
        raise Exception("file not found")
    return df


def sort_df_by_date(df, stop_date: datetime) -> pd.DataFrame:
    """Принимает датафрейм и дату окончания анализа, возвращает датафрейм с датами в диапозоне даты окончания
    и первым числом месяца"""

    month = stop_date.month
    year = stop_date.year
    start_date = datetime.datetime(year, month, 1)
    sorted_df = df.loc[(df["Номер карты"].notnull()) & (df["Статус"] == "OK")]
    sorted_df["Дата операции"] = pd.to_datetime(sorted_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    sorted_df = sorted_df[(sorted_df["Дата операции"] >= start_date) & (sorted_df["Дата операции"] <= stop_date)]

    return sorted_df


def get_card_info(df, stop_date: datetime) -> list[dict]:
    """Возвращает информацию по каждой карте от 1 числа месяца до указанной даты"""

    sorted_df = sort_df_by_date(df, stop_date)
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


def get_top_five(df, stop_date) -> list[dict]:
    """Возвращает топ 5 оперций от 1 числа месяца до указанной даты"""

    sorted_data = sort_df_by_date(df, stop_date)

    sorted_data["Сумма платежа"] = sorted_data["Сумма платежа"].astype(float)
    sorted_data = sorted_data.sort_values("Сумма платежа", key=lambda x: abs(x), ascending=False)
    top_five_list = []
    count = 0
    for index, row in sorted_data.iterrows():
        top_five_list.append({
  "date": row["Дата операции"].strftime("%d-%m-%Y %H:%M:%S"),
  "amount": row["Сумма платежа"],
  "category": row["Категория"],
  "description": row["Описание"]
})

    top_five_list = top_five_list[0:5]

    return top_five_list
