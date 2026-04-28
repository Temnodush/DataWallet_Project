import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from config import PATH_TO_EXCEL

# Создание папки для логов
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Настройка логгера
logger = logging.getLogger("services")
log_file = logs_dir / "services.log"
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def simple_search(path_to_file: str, search_query: str) -> List[Dict[str, Any]]:
    """Ищет транзакции по вхождению строки в описание или категорию (без учета регистра)."""
    logger.info(f"Запуск функции простого поиска по строке: {search_query}")
    try:
        df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям", engine="openpyxl")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {str(e)}", exc_info=True)
        raise
    mask = df["Описание"].str.contains(search_query, case=False, na=False) | df["Категория"].str.contains(
        search_query, case=False, na=False
    )

    json_str = df[mask].to_json(orient="records", force_ascii=False)
    result: List[Dict[str, Any]] = json.loads(json_str)
    logger.info("Успех! Данные отфильтрованы по описанию | категории")
    return result


def main_services(search_string):
    """Обрабатывает поисковый запрос: возвращает JSON с результатами или пустым списком."""
    if not search_string.strip():
        logger.info("Введено пустое значение.")
        return json.dumps({"Результат": []}, ensure_ascii=False)
    logger.info(f"Запускаю поиск по значению {search_string}")
    result = simple_search(PATH_TO_EXCEL, search_string)
    if result is None or result == []:
        logger.info("Поиск ничего не нашёл")
        return json.dumps({"Результат": []}, ensure_ascii=False)
    return json.dumps({"Результат": result}, ensure_ascii=False, indent=4)
