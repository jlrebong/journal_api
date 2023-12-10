import os
from pkg_resources import resource_filename
from pathlib import Path

CALENDAR_FORMAT = "%Y-%m-%d"

DATA_FORMAT_COLS = {
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
    "i": "openinterest",
}

DATA_PATH = resource_filename(__name__, "data")


if not Path(DATA_PATH).exists():
    os.makedirs(DATA_PATH)

# Cache file for PSE prices in OHLC format
PSE_CACHE_FILE = "merged_stock_data.zip"

# CSV file containing all the listed PSE companies
PSE_STOCK_TABLE_FILE = "stock_table.csv"