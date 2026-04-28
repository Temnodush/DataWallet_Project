import json
import logging
from pathlib import Path

from config import PATH_TO_EXCEL
from src.utils import (
    get_card_with_spend,
    get_currency_rates,
    get_data_time,
    get_path_and_period,
    get_stock_prices,
    get_time_for_greeting,
    get_top_transaction,
)

# Создание папки для логов
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Настройка логгера
logger = logging.getLogger("views")
log_file = logs_dir / "views.log"
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def main_views(date_time: str) -> str:
    """Формирует JSON-ответ для главной страницы с данными на основе указанной даты.
    Включает: приветствие, расходы по картам, топ транзакций, курсы валют и акций.
    """

    logger.info("Запуск функции главной страницы с заданными параметрами")
    time_period = get_data_time(date_time)
    sorted_df = get_path_and_period(PATH_TO_EXCEL, time_period)

    # 1) Приветствие

    logger.info("Запуск функции приветствия")
    greeting = get_time_for_greeting()

    # 2) По каждой карте

    logger.info("Запуск функции со списком карт по которым были расходы")
    cards = get_card_with_spend(sorted_df)

    # 3) Топ-5 транзакций по сумме платежа

    logger.info("Запуск функции по топ-транзакциям")
    top_transaction = get_top_transaction(sorted_df, 5)

    # 4) Курс валют

    logger.info("Запуск функции которая получает актуальный курс валют")
    currency_rates = get_currency_rates()

    # 5) Стоимость акций из S&P500

    logger.info("Запуск функции которая получает актуальный курс акций SP500")
    stock_prices = get_stock_prices()

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transaction,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    logger.info("Успех! Получен отфильтрованный json файл по заданным параметрам")
    return json_data
