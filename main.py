
import os
import json
import time

from API import update_database
from data_processing import search
from graph import create_graph_1, create_graph_2, create_graph_3


separator = "=" * 89

default_settings = {
    "title": "0",
    "name": "0",
    "cpv": "0",
    "amount": 5000,
}


print("Вітаємо! Ця програма допомже вам шукати аномальні тендери за допомоги API Prozorro.gov.ua")
print()
print(separator)
print()


# Завантаження налаштувань
if os.path.exists("settings.json"):
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            loaded_settings = json.load(file)

        if not isinstance(loaded_settings, dict):
            raise ValueError("Некоректний формат settings.json")

        settings = default_settings.copy()
        settings.update({
            key: value
            for key, value in loaded_settings.items()
            if key in default_settings
        })

        print("Налаштування пошуку успішно завантажено з settings.json.")

    except (OSError, json.JSONDecodeError, ValueError):
        settings = default_settings.copy()
        print("Помилка читання settings.json. Завантажено стандартні налаштування.")

else:
    settings = default_settings.copy()
    print("Файл settings.json не знайдено. Завантажено стандартні налаштування.")


print()
print(separator)


# None означає, що успішного пошуку ще не було
search_results = None

# Параметри останнього успішного пошуку
last_search_settings = None


# Основний цикл CLI
while True:

    user_input = input(
        '\nЧекаю введення наступної команди (введіть "help", щоб вивести список команд): '
    ).strip()

    parts = user_input.split(maxsplit=1)

    command = parts[0].lower() if parts else ""
    argument = parts[1].strip() if len(parts) > 1 else ""

    print()

    if command == "help":
        print("СПИСОК КОМАНД:")
        print()

        print("exit - зберегти поточне значення налаштувань у settings.json та після цього завершити виконання програми.")
        print()

        print("update_database - підгрузити з API Prozorro.gov.ua {amount} найновіших тендерів. Старі видаляються.")
        print("change_amount {НОВА КІЛЬКІСТЬ} - змінити цільову кількість тендерів у базі даних.")
        print("Будьте обережні: Знаходження тисячі тендерів триває приблизно хвилину, тому не вводьте надто великі значення.")
        print()

        print("change_title {НОВА НАЗВА} - змінити ключову підстроку, за якою здійснюється пошук по назві ТЕНДЕРУ.")
        print('Щоб не шукати за назвою тендеру, введіть нову назву "0"')

        print("change_name {НОВА НАЗВА} - змінити ключову підстроку, за якою здійснюється пошук по назві ТОВАРУ.")
        print('Щоб не шукати за назвою товару, введіть нову назву "0"')

        print("change_cpv {НОВИЙ CPV} - змінити CPV, за яким здійснюється пошук.")
        print('Щоб не шукати за CPV, введіть новий CPV "0"')
        print()

        print("check - вивести поточні налаштування пошуку.")
        print()

        print("search - провести пошук за вже заданими параметрами та вивести результати пошуку.")
        print("show {НОМЕР ТЕНДЕРА} - вивести детальну інформацію про тендер з останнього пошуку.")
        print()

        print("КОМАНДИ ГРАФІКІВ:")
        print()
        print("graph_1 - побудувати гістограму розподілу цін за одиницю товару.")
        print("graph_2 - побудувати кругову діаграму розподілу тендерів за відхиленням цін.")
        print("graph_3 {CPV} - побудувати графік топ-10 найдорожчих товарів за CPV.")
        print("Якщо CPV задано під час останнього пошуку, для graph_3 його можна не вказувати.")
        print("Перед побудовою графіків необхідно виконати команду search.")

    elif command == "exit":
        print(separator)
        break

    elif command == "change_title":
        if argument:
            settings["title"] = argument
            print(f'Успішно встановлено нову шукану в назві тендеру підстроку: "{argument}".')
        else:
            print("Помилка: введіть нову назву тендеру.")

    elif command == "change_name":
        if argument:
            settings["name"] = argument
            print(f'Успішно встановлено нову шукану в назві товару підстроку: "{argument}".')
        else:
            print("Помилка: введіть нову назву товару.")

    elif command == "change_cpv":
        if argument:
            settings["cpv"] = argument
            print(f"Успішно встановлено новий шуканий CPV: {argument}.")
        else:
            print("Помилка: введіть новий CPV.")

    elif command == "check":
        print("Поточні параметри пошуку:")
        print(f'title = "{settings["title"]}"')
        print(f'name = "{settings["name"]}"')
        print(f'cpv = "{settings["cpv"]}"')
        print(f'amount = {settings["amount"]}')

    elif command == "search":
        print("Розпочато пошук...")
        print()

        try:
            start_time = time.perf_counter()

            # Отримуємо всі знайдені тендери та медіану
            searched_df, average_price, median_price = search(
                settings["title"],
                settings["name"],
                settings["cpv"],
                True
            )

            # Отримуємо аномальні тендери
            anomalous_tenders = search(
                settings["title"],
                settings["name"],
                settings["cpv"],
                False
            )

            # Зберігаємо всі тендери для команди show
            new_results = searched_df.to_dict(orient="records")
            search_results = new_results

            # Запам'ятовуємо параметри успішного пошуку
            last_search_settings = {
                "title": settings["title"],
                "name": settings["name"],
                "cpv": settings["cpv"]
            }

            elapsed = round(time.perf_counter() - start_time, 2)

            print("Пошук завершено.")
            print(f"Операція тривала {elapsed:.2f} секунд.")
            print()
            print(f"Знайдено тендерів: {len(search_results)}")
            print()

            for number, tender in enumerate(search_results, start=1):
                print(f"[{number}] {tender.get('title', 'Без назви')}")
                print(f"Назва товару: {tender.get('desc', 'Невідомо')}")
                print(f"CPV: {tender.get('cpv', 'Невідомо')}")
                print(f"Сума: {tender.get('amount', 'Невідомо')} {tender.get('currency', '')}")
                print()

            print("Аномальні тендери:")

            anomalous_ids = {
                tender.get("id")
                for tender in anomalous_tenders
            }

            anomalies_found = False

            for number, tender in enumerate(search_results, start=1):
                if tender.get("id") in anomalous_ids:
                    anomalies_found = True

                    unit_price = tender["amount"] / tender["qty"]
                    deviation_ratio = unit_price / median_price

                    print(
                        f"[{number}] - ціна на одиницю товару у "
                        f"{deviation_ratio:.2f} рази вище за медіану."
                    )

            if not anomalies_found:
                print("Аномальних тендерів не знайдено.")

        except FileNotFoundError:
            print("Помилка: файл tenders.json не знайдено.")

        except json.JSONDecodeError:
            print("Помилка: файл tenders.json містить некоректний JSON.")

        except (OSError, KeyError, TypeError, ZeroDivisionError) as error:
            print(f"Помилка під час пошуку: {error}")

    elif command == "update_database":
        print("Ця операція може зайняти довгий час та видалить стару базу даних з тендерами.")

        confirmation = input(
            "Ви впевнені, що хочете розпочати оновлення tenders.json (yes/no): "
        ).strip().lower()

        if confirmation == "yes":
            print()
            update_database(settings["amount"])

        elif confirmation == "no":
            print("Оновлення бази даних скасовано.")

        else:
            print("Невідома відповідь. Оновлення бази даних скасовано.")

    elif command == "change_amount":
        try:
            new_amount = int(argument)

            if new_amount <= 0:
                print("Помилка: кількість тендерів повинна бути більшою за 0.")
            else:
                settings["amount"] = new_amount
                print(f"Успішно встановлено нову цільову кількість: {new_amount}")

        except ValueError:
            print("Помилка: введіть ціле число. Наприклад: change_amount 5000")

    elif command == "show":
        if search_results is None:
            print("Спочатку виконайте команду search.")

        elif not argument:
            print("Помилка: вкажіть номер тендера. Наприклад: show 3")

        elif not search_results:
            print("Останній пошук не знайшов жодного тендера.")

        else:
            try:
                number = int(argument)

                if number < 1 or number > len(search_results):
                    print(f"Помилка: тендера з номером {number} не знайдено.")

                else:
                    tender = search_results[number - 1]

                    print(f"Інформація про тендер [{number}]:")
                    print()

                    print(f"ID: {tender.get('id', 'Невідомо')}")
                    print(f"Назва тендера: {tender.get('title', 'Невідомо')}")
                    print(f"Статус: {tender.get('status', 'Невідомо')}")
                    print(f"Дата: {tender.get('date', 'Невідомо')}")
                    print()

                    print(f"Замовник: {tender.get('buyer_name', 'Невідомо')}")
                    print(f"ЄДРПОУ замовника: {tender.get('buyer_id', 'Невідомо')}")
                    print()

                    print(f"Постачальник: {tender.get('supplier_name', 'Невідомо')}")
                    print(f"Ідентифікатор постачальника: {tender.get('supplier_id', 'Невідомо')}")
                    print()

                    print(f"Назва товару: {tender.get('desc', 'Невідомо')}")
                    print(f"Код CPV: {tender.get('cpv', 'Невідомо')}")
                    print(f"Кількість: {tender.get('qty', 'Невідомо')}")
                    print(f"Одиниця вимірювання: {tender.get('unit', 'Невідомо')}")
                    print()

                    print(f"Загальна сума: {tender.get('amount', 'Невідомо')} {tender.get('currency', '')}")
                    print(f"Посилання: {tender.get('url', 'Немає')}")

            except ValueError:
                print("Помилка: номер тендера повинен бути цілим числом.")

    elif command == "graph_1":
        if search_results is None:
            print("Спочатку виконайте команду search.")

        elif not search_results:
            print("Останній пошук не знайшов жодного тендера.")

        else:
            try:
                print("Створення графіка розподілу цін...")

                fig = create_graph_1(
                    last_search_settings["title"],
                    last_search_settings["name"],
                    last_search_settings["cpv"]
                )

                if fig is None:
                    print("Недостатньо даних для побудови графіка.")
                else:
                    fig.write_html("graph_1.html", auto_open=True)
                    print("Графік успішно створено.")

            except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
                print(f"Помилка під час створення графіка: {error}")

    elif command == "graph_2":
        if search_results is None:
            print("Спочатку виконайте команду search.")

        elif not search_results:
            print("Останній пошук не знайшов жодного тендера.")

        else:
            try:
                print("Створення графіка відхилень цін...")

                fig = create_graph_2(
                    last_search_settings["title"],
                    last_search_settings["name"],
                    last_search_settings["cpv"]
                )

                if fig is None:
                    print("Недостатньо даних для побудови графіка.")
                else:
                    fig.write_html("graph_2.html", auto_open=True)
                    print("Графік успішно створено.")

            except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
                print(f"Помилка під час створення графіка: {error}")

    elif command == "graph_3":
        if search_results is None:
            print("Спочатку виконайте команду search.")

        elif not search_results:
            print("Останній пошук не знайшов жодного тендера.")

        else:
            cpv_for_graph = argument if argument else last_search_settings["cpv"]

            if cpv_for_graph == "0":
                print("Помилка: вкажіть CPV. Наприклад: graph_3 30213100-6")

            else:
                try:
                    # Перевіряємо наявність тендерів із таким CPV
                    with open("tenders.json", "r", encoding="utf-8") as file:
                        tenders = json.load(file)

                    matching_tenders = [
                        tender for tender in tenders
                        if tender.get("cpv") == cpv_for_graph
                        and isinstance(tender.get("qty"), (int, float))
                        and tender["qty"] > 0
                    ]

                    if not matching_tenders:
                        print(f"Не знайдено тендерів із CPV {cpv_for_graph}.")

                    else:
                        print(f"Створення графіка топ-10 для CPV {cpv_for_graph}...")

                        fig = create_graph_3(cpv_for_graph)

                        if fig is None:
                            print("Недостатньо даних для побудови графіка.")
                        else:
                            fig.write_html("graph_3.html", auto_open=True)
                            print("Графік успішно створено.")

                except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError, json.JSONDecodeError) as error:
                    print(f"Помилка під час створення графіка: {error}")

    else:
        print("Невідома команда. Введіть help.")

    print()
    print(separator)


# Збереження після завершення циклу
try:
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

    print()
    print("Налаштування пошуку успішно збережено у settings.json.")

except OSError as error:
    print()
    print(f"Помилка збереження settings.json: {error}")