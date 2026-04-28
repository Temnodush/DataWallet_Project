from datetime import datetime
from unittest.mock import MagicMock, patch

from src.reports import spending_by_category


@patch("src.reports.logger.info")
def test_spending_by_category_basic(mock_logger, test_transactions_df):
    category = "Супермаркеты"
    date = "2022-05-01"
    result = spending_by_category(test_transactions_df, category, date)
    assert len(result) == 2
    assert all(result["Категория"].str.strip().str.lower() == category.lower())
    mock_logger.assert_any_call(f"Запуск отчета для категории: {category}, дата отсчета: {date}")
    mock_logger.assert_any_call(f"Найдено записей: {len(result)}")


@patch("src.reports.datetime")
def test_spending_by_category_date_handling(mock_datetime, test_transactions_df):
    fixed_date = datetime(2022, 5, 1)
    mock_datetime.now.return_value = fixed_date
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    category = "Супермаркеты"
    result = spending_by_category(test_transactions_df, category)
    assert len(result) == 2


@patch("src.reports.Path.mkdir")
@patch("builtins.open", new_callable=MagicMock)
@patch("json.dumps", return_value="mocked_json")
def test_report_decorator(mock_dumps, mock_open, mock_mkdir):
    """Тест декоратора report_decorator"""
