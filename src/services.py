import json
import datetime
import logging
import pandas as pd

from src.utils import get_operations_data, sort_df_by_date

def upper_cashback(operations_data: pd.DataFrame, year: int, month: int) -> json:
    """Показывает cashback по каждой категории за указанный месяц"""
    date_obj = datetime.datetime(year, month, 1)
    year = date_obj.year
    month = date_obj.month
    if month != 12:
        last_day_of_month = date_obj.replace(month=month+1) - datetime.timedelta(days=1)
    else:
        year += 1
        last_day_of_month = date_obj.replace(year=year, month=1) - datetime.timedelta(days=1)
    sorted_df = sort_df_by_date(operations_data, last_day_of_month)

    sorted_df = sorted_df.loc[sorted_df["Сумма платежа"] < 0]
    sorted_df = sorted_df.groupby("Категория").apply(lambda x: x.agg({"Сумма платежа": "sum"}))
    sorted_df = sorted_df["Сумма платежа"].map(lambda x: round(x / (-100), 2))
    result = sorted_df.to_dict()
    result_json = json.dumps(result, indent=4, ensure_ascii=False)

    return result_json


#print(upper_cashback(get_operations_data("operations.xlsx"), 2021, 8))
