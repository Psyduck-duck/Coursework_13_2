import datetime
import json
import os
import logging

import pandas as pd
import requests
from dotenv import load_dotenv

pd.options.mode.chained_assignment = None

from data.__init__ import PATH_TO_DATA_DIRECTORY
from logs.__init__ import PATH_TO_LOGS_DIRECTORY


logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(PATH_TO_LOGS_DIRECTORY, "utils.log"),
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    encoding="utf8",
    filemode="w",
)

get_alphaventage_data_loger = logging.getLogger("get_alphaventage_data_loger")
get_greeting_loger = logging.getLogger("get_greeting_loger")
get_operations_data_loger = logging.getLogger("get_operations_data_loger")
sort_df_by_date_loger = logging.getLogger("sort_df_by_date_loger")
get_card_info_loger = logging.getLogger("get_card_info_loger")
get_top_five_loger = logging.getLogger("get_top_five_loger")



load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")

relative_path_user_setting = "../user_settings.json"
absolute_path_user_settings = os.path.abspath(relative_path_user_setting)


def get_alphavantage_data(filename: str) -> None:
    """Записывает в файл json в дирректтории data информацию об интересующих акциях"""

    get_alphaventage_data_loger.info(f"Запись данных в {filename}")

    path_to_file = os.path.join(PATH_TO_DATA_DIRECTORY, filename)
    stocks_dict = {}

    with open(absolute_path_user_settings) as file:

        get_alphaventage_data_loger.info("Получаем данный пользовательских настроек")

        data = json.load(file)
        user_stocks = data.get("user_stocks")
        user_currencies = data.get("user_currencies")

    for x in user_currencies:

        get_alphaventage_data_loger.info(f"Получаем актульный курс для {x}")

        headers = {"apikey": apilayer_API_KEY}
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={x}&amount=1"
        responce = requests.get(url, headers=headers)
        if responce.status_code != 200:

            get_alphaventage_data_loger.error("status_code != 200")

            raise ValueError("Check URL")
        data = responce.json()

        get_operations_data_loger.info(f"Запись курса для {x} в словарь")

        stocks_dict[x] = f"{round(data.get("result"), 2)} RUB"

    for i in user_stocks:

        get_alphaventage_data_loger.info(f"Получаем актуальные данные о стоимоти акций {i}")

        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={i}&interval=5min&apikey={API_KEY_alphavantage}"
        responce = requests.get(url)
        if responce.status_code != 200:

            get_alphaventage_data_loger.error("code_status != 200")

            raise ValueError("Check URL")

        get_alphaventage_data_loger.info(f"Запись данных о стоимости акций {i} в словарь")

        data = responce.json()
        stocks_dict[i] = data


    with open(path_to_file, "w", encoding="utf-8") as f:

        get_alphaventage_data_loger.info("Запись всех данных в файл. Завершение работы функции")

        json.dump(stocks_dict, f, ensure_ascii=False, indent=4)


def get_greeting(date: datetime) -> str:
    """Фукнция возвращмет приветствие в зависимости от времени суток"""

    get_greeting_loger.info("Определение и возврат актуального приветствия в зависимости от времени суток.")
    get_greeting_loger.info("Завершение работы функции")

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

    get_operations_data_loger.info(f"Данные загрузятся из {filename}")

    path_to_file = os.path.join(PATH_TO_DATA_DIRECTORY, filename)

    get_operations_data_loger.info("Попытка получить данные")

    try:
        df = pd.read_excel(path_to_file)
    except:

        get_operations_data_loger.error("Неудачная попытка, файл не найден")

        raise Exception("file not found")

    get_operations_data_loger.info("Функция возвращает данные в формате DataFrame. Завершение работы")
    return df


def sort_df_by_date(df, stop_date: datetime) -> pd.DataFrame:
    """Принимает датафрейм и дату окончания анализа, возвращает датафрейм с датами в диапозоне даты окончания
    и первым числом месяца"""

    sort_df_by_date_loger.info(f"Данные фильтруются за месяц до {stop_date}")
    sort_df_by_date_loger.info("Определение наальной даты для интервала")

    day = stop_date.day
    month = stop_date.month
    year = stop_date.year
    stop_date = datetime.datetime(year, month, day, 23, 59, 59)
    start_date = datetime.datetime(year, month, 1)

    sort_df_by_date_loger.info("Сортировка данных по статусу")

    sorted_df = df.loc[(df["Номер карты"].notnull()) & (df["Статус"] == "OK")]

    sort_df_by_date_loger.info("Сортировка данных по дате")

    sorted_df["Дата операции"] = pd.to_datetime(sorted_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    sorted_df = sorted_df[(sorted_df["Дата операции"] >= start_date) & (sorted_df["Дата операции"] <= stop_date)]
    sorted_df["Дата операции"] = sorted_df["Дата операции"].astype(str)

    sort_df_by_date_loger.info("Функция возвращает отфильтрованный датафрейм. Завершение работы")

    return sorted_df


def get_card_info(df, stop_date: datetime) -> list[dict]:
    """Возвращает информацию по каждой карте от 1 числа месяца до указанной даты"""

    get_card_info_loger.info(f"Сортировка пройдет до {stop_date}")
    get_card_info_loger.info("Сортировка данных")

    sorted_df = sort_df_by_date(df, stop_date)
    cards_info = []
    cards_uniq_numbers = sorted_df["Номер карты"].unique()

    get_card_info_loger.info("Оформление ключевой информации по каждой карте")

    for card in cards_uniq_numbers:
        card_mask = card[-4:]
        spending_operations = sorted_df.loc[(sorted_df["Номер карты"] == card) & (sorted_df["Сумма платежа"] < 0)]
        total_spending = spending_operations["Сумма платежа"].sum()
        cards_info.append(
            {
                "last_digits": card_mask,
                "total_spent": round(float(total_spending), 2) * -1,
                "cashback": round((float(total_spending) / 100), 2) * -1,
            }
        )

    get_card_info_loger.info("Функция возвращает лист словарей. Завершение работы")

    return cards_info


def get_top_five(df, stop_date) -> list[dict]:
    """Возвращает топ 5 оперций от 1 числа месяца до указанной даты"""

    get_top_five_loger.info(f"Функция сортирует до {stop_date}")
    get_top_five_loger.info("Сортировка данных")

    sorted_data = sort_df_by_date(df, stop_date)

    sorted_data["Сумма платежа"] = sorted_data["Сумма платежа"].astype(float)
    sorted_data = sorted_data.sort_values("Сумма платежа", key=lambda x: abs(x), ascending=False)
    top_five_list = []
    count = 0
    for index, row in sorted_data.iterrows():
        top_five_list.append(
            {
                "date": row["Дата операции"],
                "amount": row["Сумма платежа"],
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    top_five_list = top_five_list[0:5]

    get_top_five_loger.info("Функция возвращает топ 5 операций по модулю платежа. Завершение работы")

    return top_five_list
