import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import string
from datetime import datetime

# Глобальные переменные для хранения состояния приложения
history = []  # История сгенерированных паролей
password_entry = None  # Поле для отображения пароля
tree = None  # Таблица истории паролей
length_label = None  # Метка отображения текущей длины пароля
length_scale = None  # Ползунок длины пароля

# Глобальные переменные для чекбоксов (обязательно объявляем здесь!)
use_digits = None
use_letters = None
use_special = None

root = None  # Главное окно


def get_next_id():
    """Получение следующего ID для записи истории"""
    if not history:
        return 1
    return max(record["id"] for record in history) + 1


def update_length_label(value):
    """Обновление метки с текущей длиной пароля при движении ползунка"""
    global length_label
    length = int(float(value))
    if length_label:
        length_label.config(text=f"{length} символов")


def validate_settings():
    """Проверка корректности настроек генерации пароля"""
    global use_digits, use_letters, use_special
    if not (use_digits.get() or use_letters.get() or use_special.get()):
        messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
        return False
    return True


def generate_password():
    """Генерация случайного пароля на основе выбранных настроек"""
    global use_digits, use_letters, use_special, length_scale, password_entry

    if not validate_settings():
        return

    # Получаем длину пароля из ползунка
    length = int(length_scale.get())

    # Формируем набор символов на основе выбранных опций
    chars = ""
    if use_digits.get():
        chars += string.digits
    if use_letters.get():
        chars += string.ascii_letters
    if use_special.get():
        chars += "!@#$%^&*"

    # Проверка, что набор символов не пустой
    if not chars:
        messagebox.showerror("Ошибка", "Не выбран ни один тип символов для генерации пароля")
        return

    # Генерируем пароль
    password = ''.join(random.choice(chars) for _ in range(length))

    # Отображаем сгенерированный пароль в поле ввода
    if password_entry:
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)

    # Создаём запись для истории
    types = []
    if use_digits.get():
        types.append("Цифры")
    if use_letters.get():
        types.append("Буквы")
    if use_special.get():
        types.append("Спецсимволы")

    record = {
        "id": get_next_id(),
        "password": password,
        "length": length,
        "types": ", ".join(types),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.append(record)
    save_history()
    refresh_table()


def copy_to_clipboard():
    """Копирование пароля в буфер обмена"""
    global root, password_entry
    if not password_entry:
        return
    password = password_entry.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
    else:
        messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль")


def clear_history():
    """Очистка истории паролей"""
    if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю паролей?"):
        global history
        history = []
        save_history()
        refresh_table()
        messagebox.showinfo("Успех", "История паролей очищена")


def refresh_table():
    """Обновление таблицы с историей паролей"""
    global tree
    if not tree:
        return
    # Удаляем все текущие строки в таблице
    for item in tree.get_children():
        tree.delete(item)

    # Добавляем записи из истории в таблицу
    for record in history:
        tree.insert("", "end", values=(
            record["id"],
            record["password"],
            record["length"],
            record["types"],
            record["timestamp"]
        ))


def save_history():
    """Сохранение истории в JSON файл"""
    try:
        with open("password_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения истории: {e}")


def load_history():
    """Загрузка истории из JSON файла"""
    global history
    if os.path.exists("password_history.json"):
        try:
            with open("password_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки истории: {e}")
            history = []
    else:
        history = []


def on_closing():
    """Обработка закрытия окна с подтверждением"""
    if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти? Данные будут сохранены."):
        save_history()
        if root:
            root.destroy()


def setup_ui(root_window):
    """Настройка графического интерфейса пользователя"""
    # Объявляем ВСЕ глобальные переменные, которые будем изменять
    global root, password_entry, tree, length_label
    global use_digits, use_letters, use_special, length_scale

    root = root_window
    root.title("Random Password Generator")
    root.geometry("700x550")

    # Фрейм для настроек генерации
    settings_frame = ttk.LabelFrame(root, text="Настройки генерации")
    settings_frame.pack(pady=10, padx=10, fill="x")

    # Ползунок длины пароля (8–64 символа)
    ttk.Label(settings_frame, text="Длина пароля (8–64):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    length_scale = ttk.Scale(
        settings_frame,
        from_=8,
        to=64,
        orient="horizontal"
    )
    length_scale.set(12)  # Значение по умолчанию — 12 символов
    length_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Метка для отображения текущей длины
    length_label = ttk.Label(settings_frame, text="12 символов")
    length_label.grid(row=0, column=2, padx=5, pady=5)

    # Связываем ползунок с функцией обновления метки
    length_scale.config(command=update_length_label)

    # Инициализируем переменные для чекбоксов (После объявления global!)
    use_digits = tk.BooleanVar(value=True)
    use_letters = tk.BooleanVar(value=True)
    use_special = tk.BooleanVar(value=False)

    # Чекбоксы для выбора типов символов
    ttk.Checkbutton(settings_frame, text="Цифры (0–9)", variable=use_digits).grid(row=1, column=0, padx=5, pady=2,
                                                                                  sticky="w")
    ttk.Checkbutton(settings_frame, text="Буквы (a–z, A–Z)", variable=use_letters).grid(row=1, column=1, padx=5, pady=2,
                                                                                        sticky="w")
    ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=use_special).grid(row=1, column=2, padx=5,
                                                                                              pady=2, sticky="w")

    # Кнопка генерации пароля
    generate_button = ttk.Button(
        settings_frame,
        text="Сгенерировать пароль",
        command=generate_password
    )
    generate_button.grid(row=2, column=0, columnspan=3, pady=10)

    # Поле отображения сгенерированного пароля
    password_entry = ttk.Entry(settings_frame, width=40, font=("Courier", 12))
    password_entry.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

    # Кнопка копирования в буфер обмена
    copy_button = ttk.Button(
        settings_frame,
        text="Копировать в буфер обмена",
        command=copy_to_clipboard
    )
    copy_button.grid(row=4, column=0, columnspan=3, pady=5)

    # Фрейм для таблицы истории паролей
    history_frame = ttk.LabelFrame(root, text="История паролей")
    history_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Создание таблицы истории
    columns = ("ID", "Пароль", "Длина", "Типы символов", "Дата генерации")
    tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)

    for col in columns:
        tree.heading(col, text=col)
        if col == "Пароль":
            tree.column(col, width=200)
        elif col == "Типы символов":
            tree.column(col, width=150)
        else:
            tree.column(col, width=80)

    tree.pack(padx=5, pady=5, fill="both", expand=True)

    # Кнопка очистки истории
    clear_history_button = ttk.Button(
        history_frame,
        text="Очистить историю",
        command=clear_history
    )
    clear_history_button.pack(pady=5)

    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", on_closing)


# Основной код запуска приложения
if __name__ == "__main__":
    root = tk.Tk()

    # Загружаем историю при запуске приложения
    load_history()

    # Настраиваем пользовательский интерфейс (передаём root)
    setup_ui(root)

    # Обновляем таблицу истории после загрузки данных
    refresh_table()

    # Запускаем главный цикл обработки событий Tkinter
    root.mainloop()

