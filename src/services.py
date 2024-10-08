import datetime
import json
import os
import logging

import pandas as pd

from src.utils import get_operations_data, sort_df_by_date

from logs.__init__ import PATH_TO_LOGS_DIRECTORY

logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(PATH_TO_LOGS_DIRECTORY, "services.log"),
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    encoding="utf8",
    filemode="w",
)


get_cashbacks_by_groups_loger = logging.getLogger("get_cashbacks_by_groups_loger")


def get_cashbacks_by_groups(operations_data: pd.DataFrame, year: int, month: int) -> json:
    """Показывает cashback по каждой категории за указанный месяц"""

    get_cashbacks_by_groups_loger.debug("Составление расчетного периода")
    date_obj = datetime.datetime(year, month, 1)
    year = date_obj.year
    month = date_obj.month
    if month != 12:
        last_day_of_month = date_obj.replace(month=month + 1) - datetime.timedelta(days=1)
    else:
        year += 1
        last_day_of_month = date_obj.replace(year=year, month=1) - datetime.timedelta(days=1)

    get_cashbacks_by_groups_loger.debug("Фильтрация датафрейма по интервалу дат")

    sorted_df = sort_df_by_date(operations_data, last_day_of_month)

    get_cashbacks_by_groups_loger.debug("Сортировка по отрицательным платежам")

    sorted_df = sorted_df.loc[sorted_df["Сумма платежа"] < 0]

    get_cashbacks_by_groups_loger.debug("Группировка по категориям и суммирование")

    sorted_df = sorted_df.groupby("Категория").apply(lambda x: x.agg({"Сумма платежа": "sum"}))
    sorted_df = sorted_df["Сумма платежа"].map(lambda x: round(x / (-100), 2))
    result = sorted_df.to_dict()

    get_cashbacks_by_groups_loger.debug("Результат переводится в json формат")

    result_json = json.dumps(result, indent=4, ensure_ascii=False)

    get_cashbacks_by_groups_loger.debug("Результат возвращается в виде json строки. Завершение работы")

    return result_json


# print(get_cashbacks_by_groups(get_operations_data("operations.xlsx"), 2021, 12))
