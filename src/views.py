import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from data.__init__ import PATH_TO_DATA_DIRECTORY

load_dotenv()
API_KEY_alphavantage = os.getenv("API_KEY_alphavantage")
apilayer_API_KEY = os.getenv("apilayer_API_KEY")
