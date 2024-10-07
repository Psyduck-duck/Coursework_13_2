import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (get_alphavantage_data, get_card_info, get_greeting, get_operations_data, get_top_five,
                       sort_df_by_date)


@pytest.fixture
def some_data():
    return [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 160.89,
        },
        {
            "Дата операции": "12.09.2021 01:23:42",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*5091",
            "Статус": "OK",
            "Сумма операции": -564.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -564.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Различные товары",
            "MCC": 5399.0,
            "Описание": "Ozon.ru",
            "Бонусы (включая кэшбэк)": 5,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 564.0,
        },
        {
            "Дата операции": "10.10.2021 17:50:30",
            "Дата платежа": "30.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 5046.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 5046.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 123,
            "Категория": "Пополнения",
            "MCC": 1234,
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 5046.0,
        },
    ]


def test_get_greeting():
    date_obj_night = datetime.datetime(2023, 11, 13, 23, 11, 11)
    date_obj_day = datetime.datetime(2023, 11, 11, 12, 00, 00)
    date_obj_morning = datetime.datetime(2023, 11, 11, 6)
    assert get_greeting(date_obj_night) == "Доброй ночи"
    assert get_greeting(date_obj_day) == "Добрый день"
    assert get_greeting(date_obj_morning) == "Доброе утро"


@patch("src.utils.pd.read_excel")
def test_get_operations_data(mock_read):
    mock_read.return_value = pd.DataFrame({"test1": [1], "test2": [2]})
    assert get_operations_data("../data/operations.xlsx").to_dict(orient="records") == [{"test1": 1, "test2": 2}]


def test_get_operations_data_invalid_path():
    with pytest.raises(Exception):
        get_operations_data("../data/nofile.xlxs")


def test_sort_df_by_date(some_data):
    df = pd.DataFrame(some_data)
    date_obj_1 = datetime.datetime(2021, 10, 15, 0, 0, 0)
    date_obj_2 = datetime.datetime(2021, 12, 31, 0, 0, 0)
    assert sort_df_by_date(df, date_obj_1).to_dict(orient="records") == [
        {
            "Дата операции": "2021-10-10 17:50:30",
            "Дата платежа": "30.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 5046.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 5046.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 123,
            "Категория": "Пополнения",
            "MCC": 1234.0,
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 5046.0,
        }
    ]

    assert sort_df_by_date(df, date_obj_2).to_dict(orient="records") == [
        {
            "Дата операции": "2021-12-31 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 160.89,
        }
    ]


def test_get_card_info(some_data):
    df = pd.DataFrame(some_data)
    date_obj = datetime.datetime(2021, 9, 15, 0, 0, 0)
    assert get_card_info(df, date_obj) == [{"last_digits": "5091", "total_spent": 564.0, "cashback": 5.64}]


def test_get_card_info_no_operations(some_data):
    df = pd.DataFrame(some_data)
    date_obj = datetime.datetime(2024, 9, 15, 0, 0, 0)
    assert get_card_info(df, date_obj) == []


def test_get_top_five(some_data):
    df = pd.DataFrame(some_data)
    date_obj = datetime.datetime(2021, 9, 15, 0, 0, 0)
    assert get_top_five(df, date_obj) == [
        {"date": "2021-09-12 01:23:42", "amount": -564.0, "category": "Различные товары", "description": "Ozon.ru"}
    ]


def test_get_top_five_no_operations(some_data):
    df = pd.DataFrame(some_data)
    date_obj = datetime.datetime(2024, 9, 15, 0, 0, 0)
    assert get_top_five(df, date_obj) == []
