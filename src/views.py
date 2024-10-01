import datetime
import os
import requests
import pandas as pd
import json

from data.__init__ import PATH_TO_DATA_DIRECTORY

from dotenv import load_dotenv

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

        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={i}&interval=5min&apikey={API_KEY_alphavantage}'
        responce = requests.get(url)
        if responce.status_code != 200:
            raise ValueError("Check URL")
        data = responce.json()
        stocks_dict[i] = data

    with open(path_to_file, "w", encoding="utf-8") as f:
        json.dump(stocks_dict, f, ensure_ascii=False, indent=4)


#######################################################################################################

get_alphavantage_data("user_financial_info.json")

#with open("../user_settings.json") as file:
    #data = json.load(file)
    #print(data.get("user_stocks"))
