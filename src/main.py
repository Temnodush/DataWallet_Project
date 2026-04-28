import pandas as pd

from config import PATH_TO_EXCEL
from src.reports import spending_by_category
from src.services import main_services
from src.views import main_views

if __name__ == "__main__":
    """Точка входа: запускает главную страницу, поиск и отчет по категориям."""
    print("==================Главная страница==================")
    print(main_views("2018-04-22 18:16:00"))
    search_string = input("Введите слово для поиска по описанию или категории\n")
    print("==================Сервисы==================")
    print(main_services(search_string))
    df = pd.read_excel(PATH_TO_EXCEL)
    result = spending_by_category(df, "Супермаркеты", "2021-12-31")
    print("==================Отчёт по тратам==================")
    print(result)
