import datetime
import json
from functools import wraps
from src.utils import get_operations_data
import logging
import os

from logs.__init__ import PATH_TO_LOGS_DIRECTORY

import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(PATH_TO_LOGS_DIRECTORY, "reports.log"),
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    encoding="utf8",
    filemode="w",
)

log_loger = logging.getLogger("masks_card_loger")
spending_by_category_loger = logging.getLogger("spending_by_category")


def log(filename=""):
    """Декоратор регистрирует результат выполнения функций"""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if filename:
                log_loger.info(f"Запись результата произойдет в {filename}")

                with open(filename, "w", encoding="utf8") as file:
                    try:
                        result = func(*args, **kwargs)
                        file.write(f"{func.__name__} {result}")

                        log_loger.info(f"Запись результата работы функции {func}")

                    except Exception as e:
                        log_loger.error(f"Вызов исключения {e}")

                        file.write(f"{func.__name__} error: {type(e).__name__}. Input: ({args}, {kwargs})")
            else:
                log_loger.info(f"Вывод основных данных работы {func} произойдет в консоль")
                try:
                    log_loger.info(f"Попытка работы функции {func}")
                    result = func(*args, **kwargs)
                    log_loger.info("Печать сновных сведений")
                    print(f"{func.__name__} {result}")
                except Exception as e:
                    log_loger.error(f"Вызвано исключения {e}")
                    print(f"{func.__name__} error: {type(e).__name__}. Input: ({args}, {kwargs})")
            return result

        return inner

    return wrapper


def spending_by_category(df: pd.DataFrame, name_category: str, date: str = None) -> pd.DataFrame:
    """фильтрует датафрейм по дате (последние три месяца от указанной даты) и совпадению в категории"""

    if not date:
        spending_by_category_loger.info("Конечной датой для анализа выбрана текущая дата")
        stop_date = datetime.datetime.now()
    else:
        spending_by_category_loger.info(f"Конечной датой для анализа выбрана {date}")
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

    spending_by_category_loger.info("Датафрейм отфильтрован по статусу")

    sorted_df["Дата операции"] = pd.to_datetime(sorted_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    spending_by_category_loger.info("Колонка 'Дата операции' переведена в формат datetime")

    sorted_df = sorted_df[(sorted_df["Дата операции"] >= start_date) & (sorted_df["Дата операции"] <= stop_date)]

    spending_by_category_loger.info("Датафрейм отфильтрован по дате")

    sorted_df = sorted_df.loc[sorted_df["Категория"] == name_category]

    spending_by_category_loger.info("Датафрейм отфильтрован по категории")

    sorted_df["Дата операции"] = sorted_df["Дата операции"].astype(str)

    spending_by_category_loger.info("Колонка 'Дата операции' переведена в формат str. Функция завершает работу")

    return sorted_df
