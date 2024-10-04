import json
import pandas as pd
import datetime
from functools import wraps


def log(filename=""):
    """Декоратор регистрирует детали выполнения функций"""

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



