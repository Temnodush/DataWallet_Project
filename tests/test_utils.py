from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import (
    get_card_with_spend,
    get_currency_rates,
    get_data_time,
    get_path_and_period,
    get_stock_prices,
    get_top_transaction,
    load_user_settings,
)


@patch("builtins.open")
@patch("json.load")
def test_load_user_settings_success(mock_json_load, mock_open):
    mock_json_load.return_value = {"key": "value"}
    result = load_user_settings()
    assert result == {"key": "value"}


@patch("builtins.open", side_effect=Exception("Error"))
def test_load_user_settings_error(mock_open):
    result = load_user_settings()
    assert result == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "TSLA"],
    }


@patch("requests.get")
def test_get_currency_rates_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 75.5}, "EUR": {"Value": 85.0}}}
    mock_get.return_value = mock_response
    result = get_currency_rates()
    assert len(result) == 2
    assert result[0]["currency"] == "USD"


@patch("requests.get", side_effect=Exception("Error"))
def test_get_currency_rates_error(mock_get):
    result = get_currency_rates()
    assert result == []


@patch("requests.get", side_effect=Exception("Error"))
def test_get_stock_prices_error(mock_get):
    result = get_stock_prices()
    assert len(result) == 5
    assert "error" in result[0]


def test_get_data_time():
    result = get_data_time("2023-01-15 14:30:00")
    assert result == ["01.01.2023 14:30:00", "15.01.2023 14:30:00"]


@patch("pandas.read_excel")
def test_get_path_and_period(mock_read):
    test_data = pd.DataFrame(
        {
            "Дата операции": [
                "05.01.2023 10:00:00",
                "15.01.2023 12:00:00",
                "01.02.2023 08:00:00",
            ],
            "Номер карты": ["1234", "5678", "9012"],
            "Сумма операции": [-1000, 500, -2000],
        }
    )
    mock_read.return_value = test_data

    result = get_path_and_period("dummy.xlsx", ["01.01.2023 00:00:00", "31.01.2023 23:59:59"])
    assert len(result) == 2
    assert pd.api.types.is_datetime64_any_dtype(result["Дата операции"])


def test_get_card_with_spend(mock_excel_data_params):
    result = get_card_with_spend(mock_excel_data_params)
    assert len(result) == 2
    assert result[0]["last_digits"] == "3456"


def test_get_top_transaction(mock_excel_data_params):
    result = get_top_transaction(mock_excel_data_params, 2)
    assert len(result) == 2
    assert float(result[0]["amount"]) < 0


@pytest.mark.parametrize(
    "time_str, expected",
    [
        ("05:00:00", "Доброе утро"),
        ("11:59:59", "Доброе утро"),
        ("12:00:00", "Добрый день"),
        ("17:59:59", "Добрый день"),
        ("18:00:00", "Добрый вечер"),
        ("21:59:59", "Добрый вечер"),
        ("22:00:00", "Доброй ночи"),
        ("04:59:59", "Доброй ночи"),
    ],
)
def test_get_time_for_greeting(time_str, expected):
    with patch("src.utils.datetime") as mock_datetime:
        test_date = datetime(2023, 1, 1, int(time_str.split(":")[0]))
        mock_datetime.now.return_value = test_date

        from src.utils import get_time_for_greeting

        assert get_time_for_greeting() == expected
