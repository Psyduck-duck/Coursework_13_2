import datetime
import json
from functools import wraps
from src.utils import get_operations_data

import pandas as pd


def log(filename=""):
    """Декоратор регистрирует результат выполнения функций"""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if filename:
                with open(filename, "w", encoding="utf8") as file:
                    try:
                        result = func(*args, **kwargs)
                        file.write(f"{func.__name__} {result}")
                    except Exception as e:
                        file.write(f"{func.__name__} error: {type(e).__name__}. Input: ({args}, {kwargs})")
            else:
                try:
                    result = func(*args, **kwargs)
                    print(f"{func.__name__} {result}")
                except Exception as e:
                    print(f"{func.__name__} error: {type(e).__name__}. Input: ({args}, {kwargs})")
            return result

        return inner

    return wrapper


def spending_by_category(df: pd.DataFrame, name_category: str, date: str = None) -> pd.DataFrame:
    """фильтрует датафрейм по дате (последние три месяца от указанной даты) и совпадению в категории"""

    if not date:
        stop_date = datetime.datetime.now()
    else:
        stop_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    stop_month = stop_date.month
    stop_year = stop_date.year
    stop_day = stop_date.day
    start_month = stop_month - 3
    start_year = stop_year
    if start_month <= 0:
        start_month = 12 - abs(start_month)
        start_year = stop_year - 1
    start_date = datetime.datetime(year=start_year, month=start_month, day=stop_day)

    sorted_df = df.loc[df["Статус"] == "OK"]
    sorted_df["Дата операции"] = pd.to_datetime(sorted_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    sorted_df = sorted_df[(sorted_df["Дата операции"] >= start_date) & (sorted_df["Дата операции"] <= stop_date)]

    sorted_df = sorted_df.loc[sorted_df["Категория"] == name_category]

    sorted_df["Дата операции"] = sorted_df["Дата операции"].astype(str)

    return sorted_df
