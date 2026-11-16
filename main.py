
import os
import json

from API import update_database
from data_processing import search


separator = "=" * 89

default_settings = {
    "title": "0",
    "name": "0",
    "cpv": "0",
    "threshold": 1.5,
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


search_results = []
analysis_mode = False

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
        print('Щоб не шукати за назвою товару, введіть новий CPV "0"')
        print()

        print("check - вивести поточні налаштування пошуку.")
        print()

        print("search - провести пошук за вже заданими параметрами, вивести результати пошуку, перевести програму в режим АНАЛІЗУ.")

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
        print(f'threshold = {settings["threshold"]}')
        print(f'amount = {settings["amount"]}')


    elif command == "search":
        print("Розпочато пошук...")
        print()

        search_results = []
        analysis_mode = False

        try:
            search_results = search(
                settings["title"],
                settings["name"],
                settings["cpv"]
            )

            analysis_mode = True

            print("Пошук завершено.")
            print()
            print(f"Знайдено тендерів: {len(search_results)}")
            print()

            for number, tender in enumerate(search_results, start=1):
                print(f"[{number}] {tender.get('title', 'Без назви')}")
                print(f"Назва товару: {tender.get('desc', 'Невідомо')}")
                print(f"CPV: {tender.get('cpv', 'Невідомо')}")
                print(f"Сума: {tender.get('amount', 'Невідомо')} {tender.get('currency', '')}")
                print()

        except FileNotFoundError:
            print("Помилка: файл tenders.json не знайдено.")

        except json.JSONDecodeError:
            print("Помилка: файл tenders.json містить некоректний JSON.")

        except (OSError, KeyError, TypeError) as error:
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
        if not analysis_mode:
            print("Спочатку виконайте команду search.")

        elif not argument:
            print("Помилка: вкажіть номер тендера. Наприклад: show 3")

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


    elif command == "end_analysis":
        print("Режим аналізу поки не реалізований.")

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
