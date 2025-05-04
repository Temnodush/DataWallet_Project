import json
import logging
from unittest.mock import patch

import pytest

from src.services import logger, logs_dir, main_services, simple_search


@pytest.mark.parametrize(
    "query, expected_count, description",
    [
        ("магазин", 2, "Базовый поиск"),
        ("МаГаЗиН", 2, "Поиск без учета регистра"),
        ("несуществующий", 0, "Пустой результат"),
    ],
)
def test_simple_search_cases(query, expected_count, description, mock_excel_data):
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = mock_excel_data
        from src.services import simple_search

        result = simple_search("any_path", query)
        assert len(result) == expected_count


def test_simple_search_error_handling():
    with (
        patch("pandas.read_excel") as mock_read,
        patch("src.services.logger.error") as mock_error,
    ):
        mock_read.side_effect = Exception("File error")
        with pytest.raises(Exception):
            simple_search("bad_path", "test")
        mock_error.assert_called_once_with("Ошибка при чтении файла: File error", exc_info=True)


def test_main_services_empty_search(mock_path):
    with (
        patch("src.services.PATH_TO_EXCEL", mock_path),
        patch("src.services.logger") as mock_logger,
    ):
        result = main_services("   ")
        data = json.loads(result)
        assert data == {"Результат": []}
        mock_logger.info.assert_called_with("Введено пустое значение.")


def test_main_services_success(mock_excel_data, mock_path):
    with (
        patch("pandas.read_excel") as mock_read,
        patch("src.services.PATH_TO_EXCEL", mock_path),
    ):
        mock_read.return_value = mock_excel_data
        from src.services import main_services

        result = main_services("перевод")
        data = json.loads(result)
        assert len(data["Результат"]) == 2


def test_main_services_no_results(mock_excel_data, mock_path):
    with (
        patch("pandas.read_excel") as mock_read,
        patch("src.services.PATH_TO_EXCEL", mock_path),
    ):
        mock_read.return_value = mock_excel_data
        result = main_services("несуществующий запрос")
        data = json.loads(result)
        assert data == {"Результат": []}


def test_logs_file_creation():
    assert logs_dir.exists()
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
