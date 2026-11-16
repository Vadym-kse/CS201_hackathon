print('Вітаємо! Ця програма допоможе вам шукати аномальні тендери за допомоги API Prozorro.gov.ua')
# print('='*40)
# print('Налаштування пошуку успішно завантажено з settings.json.')
# print('='*40)
print('Чекаю введення наступної команди (введіть "help", щоб вивести список команд):')

settings = {
    "title": "0",
    "name": "0",
    "cpv": "0",
    "threshold": 1.5
}
# threshold ПОРІГ ДЛЯ МІНІМАЛЬНОГО ПОШУКУ АНОМАЛІЙ

while True:

    user_input = input("\nВведіть команду: ").strip()

    parts = user_input.split(maxsplit=1)

    if len(parts) > 0:
        command = parts[0].lower()
    else:
        command = ""

    if len(parts) > 1:
        argument = parts[1].strip()
    else:
        argument = ""

    if command == "help":
        print("Список доступних команд:")
        print("help - показати список команд")
        print("exit - завершити програму")
        print('check - вивести поточні налаштування пошуку')
        print('')
        print("change_title {НОВА НАЗВА} - змінити ключову підстроку, за якою здійснюється пошук по назві ТЕНДЕРУ. \n Щоб не шукати за назвою тендеру, введіть нову назву '0'")
        print('change_name {НОВА НАЗВА} - змінити ключову підстроку, за якою здійснюється пошук по назві ТОВАРУ. \n Щоб не шукати за назвою товару, введіть нову назву "0"')
        print('change_cpv {НОВИЙ CPV} - змінити CPV, за яким здійснюється пошук. \n Щоб не шукати за назвою товару, введіть новий CPV "0"')

    elif command == "exit":
        print("Завершення програми...")
        break

    elif command == "check":
        print("Поточні налаштування пошуку:")
        print("Назва тендера:", settings["title"])
        print("Назва товару:", settings["name"])
        print("Код CPV:", settings["cpv"])
        print("Поріг аномалії:", settings["threshold"])


    elif command == "change_title":
        if argument:
            settings["title"] = argument
            print("Нову назву тендера встановлено:", argument)
        else:
            print("Вкажіть назву після команди change_title.")

    elif command == "change_name":
        if argument:
            settings["name"] = argument
            print("Нову назву товару встановлено:", argument)
        else:
            print("Вкажіть назву після команди change_name.")

    elif command == "change_cpv":
        if argument:
            settings["cpv"] = argument
            print("Новий CPV встановлено:", argument)
        else:
            print("Вкажіть код після команди change_cpv.")

    else:
        print("Невідома команда. Введіть help.")