import pytest
import pandas as pd
import datetime

from src.reports import log, spending_by_category


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
            "Кэшбэк": 123.0,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 160.89,
        },
        {
            "Дата операции": "12.12.2021 01:23:42",
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
            "Дата операции": "10.12.2021 17:50:30",
            "Дата платежа": "10.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 5046.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 5046.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 123,
            "Категория": "Супермаркеты",
            "MCC": 1234,
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 5046.0,
        },
    ]


def test_log_decorator_without_file_name(capsys):
    @log()
    def some_func(*args, **kwargs):
        result = 0
        for i in args:
            result += i
        return result + kwargs["y"]

    some_func(1, y=0)
    captured = capsys.readouterr()
    assert captured.out == "some_func 1\n"


def test_log_decorator_without_file_name_Exeption(capsys):
    @log()
    def some_func(*args, **kwargs):
        result = 0
        for i in args:
            result += i
        return result + kwargs["y"]

    try:
        some_func(1, y="0")
    except:
        captured = capsys.readouterr()
        assert captured.out == "some_func error: TypeError. Input: ((1,), {'y': '0'})\n"


def test_log_decorator_with_filename():
    @log("filename.txt")
    def some_func():
        return None

    some_func()
    with open("filename.txt", "r", encoding="utf8") as file:
        content = file.read()
        assert content == "some_func None"


def test_log_decorator_with_filename_Exeption():
    @log("filename.txt")
    def some_func(*args, **kwargs):
        result = 0
        for i in args:
            result += i
        return result + kwargs["y"]

    try:
        some_func(1, y="0")
    except:
        with open("filename.txt", "r", encoding="utf8") as file:
            content = file.read()
            assert content == "some_func error: TypeError. Input: ((1,), {'y': '0'})"


def test_spending_by_category(some_data):
    df = pd.DataFrame(some_data)
    result = spending_by_category(df, "Супермаркеты", "2022-1-1 12:12:12")
    result_dict = result.to_dict(orient="records")
    assert result_dict == [
        {
            "Дата операции": "2021-12-31 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": 123.0,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 160.89,
        },
        {
            "Дата операции": "2021-12-10 17:50:30",
            "Дата платежа": "10.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 5046.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 5046.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 123.0,
            "Категория": "Супермаркеты",
            "MCC": 1234.0,
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 5046.0,
        }
    ]
