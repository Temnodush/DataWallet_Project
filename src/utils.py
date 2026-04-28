import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from config import PATH_TO_USER_SETTINGS

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY не найден в .env")

# Создание папки для логов
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Настройка логгера
logger = logging.getLogger("utils")
log_file = logs_dir / "utils.log"
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


load_dotenv()


main_path = os.path.dirname(os.path.abspath(__file__))

# ================== Основные/Общие функции. ==================


def load_user_settings() -> dict:
    """Загружает пользовательские настройки из JSON-файла.
    Возвращает настройки по умолчанию при ошибке."""
    try:
        with open(PATH_TO_USER_SETTINGS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {str(e)}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}


# ================== Функции для модуля views.py ==================


def get_currency_rates() -> List[Dict]:
    """Возвращает курсы валют из API ЦБ РФ для валют, указанных в настройках пользователя."""
    settings = load_user_settings()
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        rates = response.json()["Valute"]
        return [
            {"currency": curr, "rate": rates[curr]["Value"]} for curr in settings["user_currencies"] if curr in rates
        ]
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return []


def get_stock_prices() -> List[Dict]:
    """Получает текущие цены акций через API для бумаг из настроек пользователя."""
    results = []
    settings = load_user_settings()
    symbols = ",".join(settings["user_stocks"])  # Объединяем символы через запятую

    try:
        url = "https://api.twelvedata.com/price"
        params = {"symbol": symbols, "apikey": API_KEY, "format": "JSON"}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for stock in settings["user_stocks"]:
            if stock in data:
                results.append({"stock": stock, "price": float(data[stock]["price"])})
            else:
                logger.warning(f"Данные для {stock} не найдены")
                results.append({"stock": stock, "price": None, "error": "Данные не найдены"})

    except Exception as e:
        logger.error(f"Ошибка при получении данных: {str(e)}")
        return [{"stock": s, "error": str(e)} for s in settings["user_stocks"]]

    return results


def get_time_for_greeting() -> str:
    """Возвращает приветствие (Доброе утро/день/вечер/ночь) в зависимости от текущего часа системы."""
    logger.info("Запуск функции приветствия")
    user_datetime_hour = datetime.now().hour

    if 5 <= user_datetime_hour < 12:
        logger.info("Успех! Доброе утро")
        return "Доброе утро"
    elif 12 <= user_datetime_hour < 18:
        logger.info("Успех! Добрый день")
        return "Добрый день"
    elif 18 <= user_datetime_hour < 22:
        logger.info("Успех! Добрый вечер")
        return "Добрый вечер"
    else:
        logger.info("Успех! Доброй ночи")
        return "Доброй ночи"


def get_data_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """Преобразует строку даты-времени в два формата: начало месяца и исходную дату."""

    logger.info(f"Запуск функции изменения формата даты и времени с аргументами {date_time} и {date_format}")
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)

    logger.info("Успех! Данные даты и времени успешно изменены")
    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S"),
    ]


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """Загружает данные из Excel и возвращает транзакции за указанный период."""

    logger.info(f"Запуск функции среза по дате в excel файле с аргументами {path_to_file} и {period_date}")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
    filter_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    sorted_df = filter_df.sort_values(by="Дата операции", ascending=True)

    logger.info("Успех! Получен срез даты")
    return sorted_df


def get_card_with_spend(sorted_df: DataFrame) -> List[Dict[str, Any]]:
    """Возвращает список карт с суммами расходов и кэшбэком (1% от суммы в RUB)."""

    logger.info("Запуск функции со списком карт по которым были расходы.")
    card_spend_transactions = []
    card_sorted = sorted_df[["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]]
    for index, row in card_sorted.iterrows():
        if row["Сумма операции"] < 0:
            card_spend_transactions.append(
                {
                    "last_digits": str(row["Номер карты"])[-4:],
                    "total_spent": row["Сумма операции с округлением"],
                    "cashback": abs(row["Сумма операции с округлением"]) // 100,
                }
            )

    logger.info("Успех! Данные получены без ошибок")
    return card_spend_transactions


def get_top_transaction(sorted_df: DataFrame, get_top: int) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по сумме платежа (только расходы)."""

    logger.info("Запуск функции по топ-транзакциям.")
    top_pay_transactions = []
    sorted_pay_df = sorted_df[sorted_df["Сумма операции"] < 0].sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay_df.head(get_top)
    top_transactions_sorted = top_transactions[["Дата платежа", "Сумма операции", "Категория", "Описание"]]
    for index, row in top_transactions_sorted.iterrows():
        transaction = {
            "date": f"{row['Дата платежа']}",
            "amount": f"{row['Сумма операции']}",
            "category": f"{row['Категория']}",
            "description": f"{row['Описание']}",
        }
        top_pay_transactions.append(transaction)
    logger.info("Успех! Получен топ-5 по сумме платежа")
    return top_pay_transactions
