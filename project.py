import os
import re
import csv
from pathlib import Path


class PriceMachine:
    def __init__(self, directory):
        self.directory = directory
        self.results = {}
        self.export_file = "output.html"

    def load_prices(self):
        """Загружает цены из CSV файлов в указанном директории."""
        self._scan_directory()
        return self.results

    def _scan_directory(self):
        """Сканирует директорию на наличие файлов с ценами."""
        all_files = list(Path(self.directory).glob("*price*.csv"))
        for file in all_files:
            if re.search(r'\bprice\b', file.stem):  # Проверяет, что имя файла содержит "price"
                with open(file, encoding="utf-8") as input_file:
                    reader = csv.DictReader(input_file, delimiter=';')
                    self._parse_csv(reader, file.stem)

    def _parse_csv(self, reader, file_stem):
        """Парсит CSV файл и добавляет данные о ценах и продуктах в результаты."""
        print(f"Columns found: {reader.fieldnames}")
        product_column = None
        price_column = None
        weight_column = None

        # Определяем, какие колонки соответствуют продукту, цене и весу
        for index, column in enumerate(reader.fieldnames):
            if column in ["название", "продукт", "товар", "наименование"]:
                product_column = index
            elif column in ["цена", "розница"]:
                price_column = index
            elif column in ["фасовка", "масса", "вес"]:
                weight_column = index

        if product_column is not None and price_column is not None and weight_column is not None:
            # Читаем строки из CSV и сохраняем данные о продуктах
            for row in reader:
                product = row[reader.fieldnames[product_column]]
                price = float(row[reader.fieldnames[price_column]])
                weight = float(row[reader.fieldnames[weight_column]])
                print(f"Найден продукт: {product}, цена: {price}, вес: {weight}")
                if product in self.results:
                    current_product = self.results[product]
                    current_product["prices"].append((price, weight))
                    current_product["filenames"].add(file_stem)
                else:
                    self.results[product] = {"prices": [(price, weight)], "filenames": {file_stem}}

    def export_to_html(self):
        """Экспортирует результаты в HTML файл."""
        with open(self.export_file, "w", encoding="utf-8") as output_file:
            output_file.write(
                "<!DOCTYPE html>\n<html>\n<head>\n"
                "<meta charset=\"utf-8\">\n"  # Добавлено для корректного отображения кириллицы
                "<title>Позиции продуктов</title>\n"
                "</head>\n<body>\n<table>\n<tr>\n"
                "<th>Номер</th>\n<th>Название</th>\n"
                "<th>Цена</th>\n<th>Фасовка</th>\n"
                "<th>Файл</th>\n<th>Цена за кг.</th>\n</tr>\n")
            count = 1
            for product, data in self.results.items():
                prices = data["prices"]
                filenames = data["filenames"]
                for (price, weight) in prices:
                    price_per_kg = price / weight if weight > 0 else 0
                    for filename in filenames:
                        output_file.write(
                            f"\t<tr><td>{count}</td><td>{product}"
                            f"</td><td>{price}</td><td>{weight}</td>"
                            f"<td>{filename}</td><td>{price_per_kg:.2f}</td></tr>\n")
                    count += 1
            output_file.write("\n</table>\n</body>\n</html>")

    def find_text(self, search_term):
        """Ищет продукты по заданному текстовому запросу."""
        found_positions = []
        for product, data in self.results.items():
            if search_term.lower() in product.lower():
                found_positions.append((product, data["prices"], data["filenames"]))
                print(f"Найден товар: {product}")
        return found_positions

    def display_results(self, search_term):
        """Отображает результаты поиска продуктов."""
        positions = self.find_text(search_term)
        sorted_positions = []

        for product, prices, filenames in positions:
            for price, weight in prices:
                price_per_kg = price / weight if weight > 0 else 0
                for filename in filenames:
                    sorted_positions.append((product, price, weight, filename, price_per_kg))

        sorted_positions.sort(key=lambda x: x[4])  # Сортируем по цене за кг

        print(f"{'№':<3} {'Наименование':<30} {'Цена':<10} {'Вес':<5} {'Файл':<20} {'Цена за кг.':<10}")
        for index, (product, price, weight, filename, price_per_kg) in enumerate(sorted_positions, start=1):
            print(f"{index:<3} {product:<30} {price:<10} {weight:<5} {filename:<20} {price_per_kg:<10.2f}")


if __name__ == "__main__":
    pm = PriceMachine(".\\files")  # Укажите правильный путь к директории с файлами
    pm.load_prices()  # Загружаем цены из CSV файлов
    pm.export_to_html()  # Экспортируем результаты в HTML файл

    while True:
        user_input = input("Введите текст для поиска или 'exit' для завершения: ")
        if user_input == "exit":
            break
        pm.display_results(user_input)  # Отображаем результаты поиска

    print("Работа завершена.")