import pytest
import pandas as pd

from src.reports import log, spending_by_category

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


