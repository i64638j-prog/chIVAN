import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class WeatherDiary:
    def __init__(self, window):
        self.window = window
        self.window.title("Weather Diary - Дневник погоды")
        self.window.geometry("800x600")

        self.entries = []
        self.current_file = None

        self.setup_ui()
        self.create_table()

    def setup_ui(self):
        # Frame для ввода данных
        input_frame = ttk.LabelFrame(self.window, text="Добавление записи", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=25)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)

        # Осадки
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=6, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_entry).grid(row=0, column=7, padx=10, pady=5)

        # Frame для фильтров
        filter_frame = ttk.LabelFrame(self.window, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date = ttk.Entry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5, pady=5)
        self.filter_date.insert(0, "ГГГГ-ММ-ДД")
        self.filter_date.bind("<FocusIn>", lambda e: self.filter_date.delete(0,
                                                                             tk.END) if self.filter_date.get() == "ГГГГ-ММ-ДД" else None)

        # Фильтр по температуре
        ttk.Label(filter_frame, text="Температура выше:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp = ttk.Entry(filter_frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10,
                                                                                          pady=5)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5, padx=5,
                                                                                         pady=5)

        # Frame для кнопок файловых операций
        file_frame = ttk.Frame(self.window, padding=5)
        file_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)

    def create_table(self):
        # Таблица для отображения записей
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("#", "Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("#", text="#")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Температура", text="Температура (°C)")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Осадки", text="Осадки")

        self.tree.column("#", width=40, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")
        self.tree.column("Температура", width=100, anchor="center")
        self.tree.column("Описание", width=300)
        self.tree.column("Осадки", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        try:
            temp = float(temp_str)
            return True, temp
        except ValueError:
            return False, None

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        valid_temp, temperature = self.validate_temperature(temp_str)
        if not valid_temp:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        entry = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": precipitation
        }

        self.entries.append(entry)
        self.refresh_table()

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        messagebox.showinfo("Успех", "Запись добавлена")

    def refresh_table(self, filtered_entries=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        entries_to_show = filtered_entries if filtered_entries is not None else self.entries

        for i, entry in enumerate(entries_to_show, 1):
            precip_text = "Да" if entry["precipitation"] else "Нет"
            self.tree.insert("", "end", values=(
                i,
                entry["date"],
                entry["temperature"],
                entry["description"],
                precip_text
            ))

    def apply_filter(self):
        filter_date = self.filter_date.get().strip()
        filter_temp_str = self.filter_temp.get().strip()

        filtered = self.entries.copy()

        # Фильтр по дате
        if filter_date and filter_date != "ГГГГ-ММ-ДД":
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
                return
            filtered = [e for e in filtered if e["date"] == filter_date]

        # Фильтр по температуре
        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [e for e in filtered if e["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return

        self.refresh_table(filtered)

        if filtered:
            messagebox.showinfo("Фильтр", f"Найдено {len(filtered)} записей")
        else:
            messagebox.showinfo("Фильтр", "Записей не найдено")

    def reset_filter(self):
        self.filter_date.delete(0, tk.END)
        self.filter_date.insert(0, "ГГГГ-ММ-ДД")
        self.filter_temp.delete(0, tk.END)
        self.refresh_table()

    def save_to_json(self):
        if not self.entries:
            messagebox.showwarning("Предупреждение", "Нет записей для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить дневник погоды"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.entries, f, ensure_ascii=False, indent=4)
                self.current_file = file_path
                messagebox.showinfo("Успех", f"Данные сохранены в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_from_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить дневник погоды"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_entries = json.load(f)

                # Базовая валидация загруженных данных
                for entry in loaded_entries:
                    if not all(k in entry for k in ("date", "temperature", "description", "precipitation")):
                        raise ValueError("Неверный формат данных в файле")

                self.entries = loaded_entries
                self.current_file = file_path
                self.refresh_table()
                messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей из {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")


if __name__ == "__main__":
    window = tk.Tk()
    app = WeatherDiary(window)
    window.mainloop()
