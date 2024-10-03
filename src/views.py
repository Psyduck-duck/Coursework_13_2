import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from data.__init__ import PATH_TO_DATA_DIRECTORY
from src.utils import get_alphavantage_data, get_greeting, get_operations_data, get_card_info, get_top_five

load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")


def main_page(date):
    """принимающую на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS"""


    df = get_operations_data("operations.xlsx")
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    financial_file = "user_financial_info.json"
    greeting = get_greeting(date_obj)

    #get_alphavantage_data(financial_file)

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

    return result


#result = main_page("2021-12-30 0:0:0")
#with open("result.json", "w", encoding="utf-8") as file:
    #json.dump(result, file, ensure_ascii=False, indent=4)
