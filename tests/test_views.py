import json
from unittest.mock import patch

import pandas as pd

from src.views import main_views


@patch("src.views.get_data_time")
@patch("src.views.get_path_and_period")
@patch("src.views.get_time_for_greeting")
@patch("src.views.get_card_with_spend")
@patch("src.views.get_top_transaction")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_views_success(
    mock_stocks,
    mock_rates,
    mock_top,
    mock_cards,
    mock_greeting,
    mock_period,
    mock_data_time,
    mock_transactions_df,
):
    mock_data_time.return_value = ["01.01.2023", "31.01.2023"]
    mock_period.return_value = mock_transactions_df
    mock_greeting.return_value = "Добрый день"
    mock_cards.return_value = [{"card": "data"}]
    mock_top.return_value = [{"transaction": "data"}]
    mock_rates.return_value = [{"currency": "USD"}]
    mock_stocks.return_value = [{"stock": "AAPL"}]
    result = json.loads(main_views("2023-01-15 00:00:00"))
    assert result == {
        "greeting": "Добрый день",
        "cards": [{"card": "data"}],
        "top_transactions": [{"transaction": "data"}],
        "currency_rates": [{"currency": "USD"}],
        "stock_prices": [{"stock": "AAPL"}],
    }


@patch("src.views.logger")
@patch("src.views.get_currency_rates")
def test_main_views_currency_error(mock_rates, mock_logger):
    mock_rates.return_value = []
    result = json.loads(main_views("2023-01-15 00:00:00"))
    assert result["currency_rates"] == []


@patch("src.views.logger.info")
@patch("src.views.get_data_time")
@patch("src.views.get_path_and_period")
@patch("src.views.get_time_for_greeting")
@patch("src.views.get_card_with_spend")
@patch("src.views.get_top_transaction")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_views_logging(
    mock_stocks,
    mock_rates,
    mock_top,
    mock_cards,
    mock_greeting,
    mock_period,
    mock_data_time,
    mock_logger,
):
    mock_data_time.return_value = ["01.01.2023", "31.01.2023"]
    mock_period.return_value = pd.DataFrame()
    mock_greeting.return_value = "Добрый день"
    mock_cards.return_value = []
    mock_top.return_value = []
    mock_rates.return_value = []
    mock_stocks.return_value = []
    main_views("2023-01-15 00:00:00")
    calls = [
        "Запуск функции главной страницы с заданными параметрами",
        "Запуск функции приветствия",
        "Запуск функции со списком карт по которым были расходы",
        "Запуск функции по топ-транзакциям",
        "Запуск функции которая получает актуальный курс валют",
        "Запуск функции которая получает актуальный курс акций SP500",
        "Успех! Получен отфильтрованный json файл по заданным параметрам",
    ]
    for call in calls:
        mock_logger.assert_any_call(call)


@patch("src.views.get_stock_prices")
@patch("src.views.get_data_time")
@patch("src.views.get_path_and_period")
@patch("src.views.get_time_for_greeting")
@patch("src.views.get_card_with_spend")
@patch("src.views.get_top_transaction")
@patch("src.views.get_currency_rates")
def test_main_views_stock_error(
    mock_rates,
    mock_top,
    mock_cards,
    mock_greeting,
    mock_period,
    mock_data_time,
    mock_stocks,
):
    mock_data_time.return_value = ["01.01.2023", "31.01.2023"]
    mock_period.return_value = pd.DataFrame()
    mock_greeting.return_value = "Добрый день"
    mock_cards.return_value = []
    mock_top.return_value = []
    mock_rates.return_value = []
    mock_stocks.return_value = [{"error": "Timeout"}]
    result = json.loads(main_views("2023-01-15 00:00:00"))
    assert "error" in result["stock_prices"][0]
