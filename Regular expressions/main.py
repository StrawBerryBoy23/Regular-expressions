import csv
import re
from pprint import pprint

# 1. Читаем адресную книгу в формате CSV в список contacts_list
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# Отделяем заголовок от данных для удобства обработки
header = contacts_list[0]
data = contacts_list[1:]

processed_contacts = []

# 2. Обрабатываем каждую строку (TODO 1: пункты 1-3)
for row in data:
    # --- ПУНКТ 1: Исправление ФИО ---
    # Берем первые 3 элемента, объединяем в одну строку через пробел и разбиваем обратно по пробелам.
    # Это автоматически решит проблемы вроде "ИвановИван", "Иванов Иван Иванович" или "Иванов", "", "".
    raw_name = " ".join(row[:3]).split()

    # Гарантируем, что в списке всегда ровно 3 элемента (дополняем пустыми строками, если не хватает)
    while len(raw_name) < 3:
        raw_name.append("")

    # Перезаписываем первые три колонки
    row[0], row[1], row[2] = raw_name[0], raw_name[1], raw_name[2]

    # --- ПУНКТ 2: Форматирование телефона ---
    phone = row[5]
    if phone:
        # Ищем добавочный номер (учитываем возможные варианты: доб, доб., ДОБ, с пробелом или без)
        ext_match = re.search(r'доб\.?\s*(\d+)', phone, re.IGNORECASE)
        ext = f" доб.{ext_match.group(1)}" if ext_match else ""

        # Оставляем в строке только цифры
        digits = re.sub(r'\D', '', phone)

        # Нормализация российских номеров к 11 цифрам, начинающимся с 7
        if len(digits) == 11:
            if digits.startswith('8'):
                digits = '7' + digits[1:]
        elif len(digits) == 10 and digits.startswith('9'):  # Если номер введен как 9991234567
            digits = '7' + digits

        # Если после очистки у нас корректный российский номер, форматируем его
        if len(digits) == 11 and digits.startswith('7'):
            row[5] = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}{ext}"

    processed_contacts.append(row)

# --- ПУНКТ 3: Объединение дублирующихся записей ---
merged_dict = {}
for row in processed_contacts:
    # Ключ для группировки: Фамилия и Имя в нижнем регистре (чтобы "иванов" и "Иванов" считались одним человеком)
    key = (row[0].strip().lower(), row[1].strip().lower())

    # Пропускаем полностью пустые строки, если они вдруг попались
    if not key[0] and not key[1]:
        continue

    if key not in merged_dict:
        # Если видим человека впервые, добавляем его запись в словарь
        merged_dict[key] = row
    else:
        # Если человек уже есть, объединяем данные
        existing_row = merged_dict[key]
        # Проходим по всем полям, начиная с Отчества (индекс 2) до конца строки
        for i in range(2, len(row)):
            # Если в объединенной записи поле пустое, а в текущей строке оно заполнено, берем его
            if not existing_row[i] and row[i]:
                existing_row[i] = row[i]

# Собираем итоговый список: заголовок + уникальные значения из словаря
final_contacts = [header] + list(merged_dict.values())

# TODO 2: сохраняем получившиеся данные в другой файл
# newline="" предотвращает появление лишних пустых строк при записи CSV в Windows
with open("phonebook.csv", "w", encoding="utf-8", newline="") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)

# Выводим результат для проверки
print("Обработка завершена. Результат:")
pprint(final_contacts)