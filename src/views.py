import datetime
import json
import os
import logging

import pandas as pd
import requests
from dotenv import load_dotenv

from data.__init__ import PATH_TO_DATA_DIRECTORY
from logs.__init__ import PATH_TO_LOGS_DIRECTORY
from src.utils import get_alphavantage_data, get_card_info, get_greeting, get_operations_data, get_top_five

logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(PATH_TO_LOGS_DIRECTORY, "views.log"),
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    encoding="utf8",
    filemode="w",
)

main_page_loger = logging.getLogger("main_page_loger")

load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")


def main_page(date):
    """принимающую на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS"""

    main_page_loger.info(f"Функция работает с датой {date}")
    main_page_loger.info("Получаем данный из xlsx файла")

    df = get_operations_data("operations.xlsx")
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    financial_file = "user_financial_info.json"
    greeting = get_greeting(date_obj)

    get_alphavantage_data(financial_file)

    main_page_loger.info("Обновление финансовой информации по настройкам пользователя")
    main_page_loger.info("Сбор основной информации")

    result = {}
    result["greeting"] = greeting
    result["cards"] = get_card_info(df, date_obj)
    result["top_transactions"] = get_top_five(df, date_obj)
    result["currency_rates"] = []
    result["stock_prices"] = []

    with open(os.path.join(PATH_TO_DATA_DIRECTORY, financial_file), "r", encoding="utf-8") as file:
        user_fin_info = json.load(file)

    for key, value in user_fin_info.items():
        if type(value) == str:
            result["currency_rates"].append({"currency": key, "rate": value})
        else:
            result["stock_prices"].append({"stock": key, "price": value.get("Global Quote").get("05. price")})

    result_json = json.dumps(result, indent=4, ensure_ascii=False)

    main_page_loger.info("Функция возвращает результат в виде json строки. Завершение работы")

    return result_json
