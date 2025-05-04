import json
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

# Настройка логгера
logger = logging.getLogger("reports")
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(logs_dir / "reports.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def report_decorator(filename: Optional[str] = None) -> Callable:
    """Декоратор для автоматического сохранения результатов функции в JSON-файл (папка reports/)."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            # Создаем папку reports, если её нет
            output_dir = Path(__file__).resolve().parent.parent / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)  # parents=True для вложенных путей

            # Формируем полный путь к файлу
            output_file = output_dir / (filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

            try:
                # Сохранение в JSON
                if isinstance(result, pd.DataFrame):
                    json_data = result.to_json(orient="records", force_ascii=False, indent=4)
                else:
                    json_data = json.dumps(result, ensure_ascii=False, indent=4)

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(json_data)

                logger.info(f"Отчет сохранен в файл: {output_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {str(e)}", exc_info=True)
                raise

            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Фильтрует расходы по указанной категории за последние 3 месяца от заданной даты."""
    logger.info(f"Запуск отчета для категории: {category}, дата отсчета: {date or 'текущая'}")

    try:
        # Проверка обязательных колонок
        required_columns = ["Категория", "Дата операции", "Сумма операции"]
        missing = [col for col in required_columns if col not in transactions.columns]
        if missing:
            logger.error(f"Отсутствуют колонки: {missing}")
            return pd.DataFrame()

        # Преобразование даты
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"],
            format="%d.%m.%Y %H:%M:%S",
            dayfirst=True,
            errors="coerce",
        )

        # Определение периода
        end_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - pd.DateOffset(months=3)

        # Нормализация категорий
        transactions["Категория"] = transactions["Категория"].str.strip().str.lower()
        target_category = category.strip().lower()

        # Фильтрация данных
        mask = (
            (transactions["Категория"].str.strip().str.lower() == target_category)
            & (transactions["Дата операции"].between(start_date, end_date, inclusive="both"))
            & (transactions["Сумма операции"] < 0)
        )

        filtered = transactions.loc[mask]

        logger.info(f"Найдено записей: {len(filtered)}")
        return filtered

    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
        raise
