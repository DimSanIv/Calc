#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Калькулятор для сложения и вычитания больших чисел
с интерфейсом в стиле OS/2 от IBM

Этот модуль создает графическое приложение для выполнения операций
сложения и вычитания больших чисел с возможностью исправления ошибок.
Это тест от DSK по изменениям в GetHub
"""

# Импорт стандартных библиотек
import sys
import io
import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation
import os

# Настройка кодировки для Windows консоли
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class OS2Calculator:
    """
    Класс для создания калькулятора в стиле OS/2 от IBM.
    
    Особенности:
    - Крупные кнопки, особенно для операций + и -
    - Лента вычислений (только просмотр, без редактирования)
    - Отдельное окно для отображения текущей суммы
    """
    
    def __init__(self, root):
        """
        Инициализация главного окна приложения.
        
        Args:
            root: Корневое окно Tkinter
        """
        self.root = root
        self.root.title("Калькулятор OS/2")
        self.root.geometry("320x450")
        self.root.resizable(False, False)
        
        # Стиль OS/2 - серый фон
        self.root.configure(bg='#C0C0C0')
        
        # Пытаемся изменить цвет заголовка (для Windows)
        try:
            # Для Windows можно использовать системные цвета через ttk
            import tkinter.ttk as ttk
            style = ttk.Style()
            style.theme_use('default')
        except:
            pass
        
        # Текущая сумма (используем Decimal для точности с большими числами)
        self.current_sum = Decimal('0')
        # История вычислений
        self.history = []
        # Текущий ввод
        self.current_input = ""
        # Режим ввода (ввод числа или операции)
        self.input_mode = "number"
        # Последняя операция
        self.last_operation = None
        
        self._create_widgets()
        self._create_history_window()
        self._bind_keyboard()
        
    def _create_widgets(self):
        """Создание всех виджетов интерфейса."""
        
        # === ОСНОВНОЙ КОНТЕЙНЕР ===
        main_container = tk.Frame(self.root, bg='#C0C0C0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === ОСНОВНОЙ КАЛЬКУЛЯТОР ===
        left_panel = tk.Frame(main_container, bg='#C0C0C0')
        left_panel.pack(fill=tk.BOTH, expand=True)
        
        # === ОКНО ТЕКУЩЕЙ СУММЫ ===
        sum_frame = tk.Frame(left_panel, bg='#C0C0C0', relief=tk.RAISED, bd=3)
        sum_frame.pack(padx=5, pady=(5, 5), fill=tk.X)
        
        sum_label = tk.Label(
            sum_frame,
            text="Текущая сумма:",
            bg='#C0C0C0',
            font=('MS Sans Serif', 10, 'bold'),
            anchor='w'
        )
        sum_label.pack(padx=5, pady=(5, 2), fill=tk.X)
        
        self.sum_display = tk.Label(
            sum_frame,
            text="0,00",
            bg='#FFFFFF',
            fg='#000000',
            font=('Courier', 14, 'bold'),
            relief=tk.SUNKEN,
            bd=3,
            anchor='e',
            padx=10,
            pady=5
        )
        self.sum_display.pack(padx=5, pady=(0, 5), fill=tk.X)
        
        # === ОКНО ТЕКУЩЕГО ВВОДА ===
        input_frame = tk.Frame(left_panel, bg='#C0C0C0')
        input_frame.pack(padx=5, pady=5, fill=tk.X)
        
        input_label = tk.Label(
            input_frame,
            text="Ввод:",
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            anchor='w'
        )
        input_label.pack(padx=5, pady=(0, 2), fill=tk.X)
        
        self.input_display = tk.Label(
            input_frame,
            text="0",
            bg='#FFFFFF',
            fg='#000000',
            font=('Courier', 12),
            relief=tk.SUNKEN,
            bd=2,
            anchor='e',
            padx=10,
            pady=5
        )
        self.input_display.pack(padx=5, pady=(0, 5), fill=tk.X)
        
        # === БЛОК УПРАВЛЕНИЯ ЛЕНТОЙ ===
        ribbon_control_frame = tk.Frame(left_panel, bg='#C0C0C0', relief=tk.RAISED, bd=2)
        ribbon_control_frame.pack(padx=5, pady=5, fill=tk.X)
        
        ribbon_label = tk.Label(
            ribbon_control_frame,
            text="Управление лентой:",
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            anchor='w'
        )
        ribbon_label.pack(padx=5, pady=(5, 2), fill=tk.X)
        
        ribbon_buttons_frame = tk.Frame(ribbon_control_frame, bg='#C0C0C0')
        ribbon_buttons_frame.pack(padx=5, pady=(0, 5), fill=tk.X)
        
        clear_ribbon_btn = tk.Button(
            ribbon_buttons_frame,
            text="Очистить ленту",
            command=self._clear_history,
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            relief=tk.RAISED,
            bd=2
        )
        clear_ribbon_btn.pack(side=tk.LEFT, padx=(0, 4), fill=tk.BOTH, expand=True)
        
        hide_ribbon_btn = tk.Button(
            ribbon_buttons_frame,
            text="Скрыть",
            command=self._toggle_history_window,
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            relief=tk.RAISED,
            bd=2
        )
        hide_ribbon_btn.pack(side=tk.LEFT, padx=(4, 0), fill=tk.BOTH, expand=True)
        
        # === ПАНЕЛЬ КНОПОК ===
        buttons_container = tk.Frame(left_panel, bg='#C0C0C0')
        buttons_container.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Контейнер для цифр слева и операций справа
        digits_and_ops = tk.Frame(buttons_container, bg='#C0C0C0')
        digits_and_ops.pack(fill=tk.BOTH, expand=True)
        
        # Левая часть: цифровые кнопки
        digits_frame = tk.Frame(digits_and_ops, bg='#C0C0C0')
        digits_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        
        # Первый ряд: цифры 7, 8, 9
        row1 = tk.Frame(digits_frame, bg='#C0C0C0')
        row1.pack(fill=tk.BOTH, expand=True, pady=2)
        
        for num in [7, 8, 9]:
            btn = self._create_number_button(row1, str(num))
            btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        # Второй ряд: цифры 4, 5, 6
        row2 = tk.Frame(digits_frame, bg='#C0C0C0')
        row2.pack(fill=tk.BOTH, expand=True, pady=2)
        
        for num in [4, 5, 6]:
            btn = self._create_number_button(row2, str(num))
            btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        # Третий ряд: цифры 1, 2, 3
        row3 = tk.Frame(digits_frame, bg='#C0C0C0')
        row3.pack(fill=tk.BOTH, expand=True, pady=2)
        
        for num in [1, 2, 3]:
            btn = self._create_number_button(row3, str(num))
            btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        # Четвертый ряд: 0 и другие кнопки
        row4 = tk.Frame(digits_frame, bg='#C0C0C0')
        row4.pack(fill=tk.BOTH, expand=True, pady=2)
        
        zero_btn = self._create_number_button(row4, "0")
        zero_btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        clear_btn = self._create_button(row4, "Очистить", self._clear_all, height=2)
        clear_btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        backspace_btn = self._create_button(row4, "←", self._backspace, height=2)
        backspace_btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        # Правая часть: кнопки операций
        operations_frame = tk.Frame(digits_and_ops, bg='#C0C0C0')
        operations_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(2, 0))
        
        # Кнопка сложения (+)
        add_btn = self._create_operation_button(operations_frame, "+", self._add)
        add_btn.pack(pady=2, fill=tk.BOTH, expand=True)
        
        # Кнопка вычитания (-)
        subtract_btn = self._create_operation_button(operations_frame, "-", self._subtract)
        subtract_btn.pack(pady=2, fill=tk.BOTH, expand=True)
        
        # Кнопка применения операции (=)
        equals_btn = self._create_operation_button(operations_frame, "=", self._equals)
        equals_btn.pack(pady=2, fill=tk.BOTH, expand=True)
        
    def _create_number_button(self, parent, text):
        """Создание кнопки с цифрой."""
        return self._create_button(parent, text, lambda: self._number_click(text), height=3)
    
    def _create_operation_button(self, parent, text, command):
        """Создание крупной кнопки операции."""
        font_size = 24 if text != "=" else 20
        return self._create_button(parent, text, command, height=3, font_size=font_size)
    
    def _create_button(self, parent, text, command, height=2, font_size=12):
        """
        Создание стандартной кнопки в стиле OS/2.
        
        Args:
            parent: Родительский виджет
            text: Текст на кнопке
            command: Функция-обработчик
            height: Высота кнопки (в строках текста)
            font_size: Размер шрифта
        """
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg='#C0C0C0',
            fg='#000000',
            font=('MS Sans Serif', font_size, 'bold'),
            relief=tk.RAISED,
            bd=3,
            activebackground='#D0D0D0',
            activeforeground='#000000',
            cursor='hand2'
        )
        return btn
    
    def _number_click(self, digit):
        """Обработка нажатия цифры или десятичной точки."""
        if self.input_mode == "operation":
            self.current_input = ""
            self.input_mode = "number"
        
        if digit == '.':
            # Обработка десятичной точки
            if '.' not in self.current_input:
                if not self.current_input:
                    self.current_input = "0."
                else:
                    self.current_input += "."
        elif self.current_input == "0" and digit != "0":
            self.current_input = digit
        elif self.current_input == "0" and digit == "0":
            return
        else:
            self.current_input += digit
        
        self._update_input_display()
    
    def _add(self):
        """Обработка операции сложения."""
        self._apply_operation("+")
    
    def _subtract(self):
        """Обработка операции вычитания."""
        self._apply_operation("-")
    
    def _apply_operation(self, operation):
        """Применение операции к текущей сумме."""
        if self.current_input:
            try:
                value = Decimal(self.current_input)
                if self.last_operation == "+":
                    self.current_sum += value
                elif self.last_operation == "-":
                    self.current_sum -= value
                else:
                    self.current_sum = value
                
                if self.last_operation:
                    self._add_to_history(f"{self._format_number(self.current_sum - value)} {self.last_operation} {self._format_number(value)} = {self._format_number(self.current_sum)}")
                
                self.last_operation = operation
                self.current_input = ""
                self.input_mode = "operation"
                self._update_sum_display()
                self._update_input_display()
            except (InvalidOperation, ValueError) as e:
                messagebox.showerror("Ошибка", f"Неверный ввод: {e}")
                self.current_input = ""
                self._update_input_display()
        else:
            # Если нет текущего ввода, просто запоминаем операцию
            self.last_operation = operation
    
    def _equals(self):
        """Применение операции и завершение вычисления."""
        if self.last_operation and self.current_input:
            self._apply_operation(None)
            self.last_operation = None
        elif self.current_input and not self.last_operation:
            # Просто устанавливаем текущую сумму равной введенному числу
            try:
                self.current_sum = Decimal(self.current_input)
                self._add_to_history(f"= {self._format_number(self.current_sum)}")
                self.current_input = ""
                self.input_mode = "operation"
                self._update_sum_display()
                self._update_input_display()
            except (InvalidOperation, ValueError) as e:
                messagebox.showerror("Ошибка", f"Неверный ввод: {e}")
                self.current_input = ""
                self._update_input_display()
    
    def _clear_all(self):
        """Очистка всех данных."""
        self.current_sum = Decimal('0')
        self.current_input = ""
        self.last_operation = None
        self.input_mode = "number"
        self._update_sum_display()
        self._update_input_display()
    
    def _backspace(self):
        """Удаление последней введенной цифры."""
        if self.current_input and len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        elif self.current_input:
            self.current_input = "0"
        self._update_input_display()
    
    def _update_sum_display(self):
        """Обновление отображения текущей суммы."""
        self.sum_display.config(text=self._format_number(self.current_sum))
    
    def _update_input_display(self):
        """Обновление отображения текущего ввода с форматированием."""
        if self.current_input:
            try:
                # Пробуем отформатировать число с разделителем
                value = Decimal(self.current_input)
                display_text = self._format_input_number(value)
            except (InvalidOperation, ValueError):
                # Если не число, просто показываем как есть
                display_text = self.current_input
        else:
            display_text = "0"
        self.input_display.config(text=display_text)
    
    def _format_input_number(self, number):
        """Форматирование числа для окна ввода с разделителем тысяч."""
        num_str = str(number)
        
        # Разделяем на целую и дробную части
        if '.' in num_str:
            parts = num_str.split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
        else:
            integer_part = num_str
            decimal_part = ""
        
        # Добавляем символ "'" как разделитель тысяч
        formatted = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted = "'" + formatted
            formatted = digit + formatted
        
        if decimal_part:
            formatted += "." + decimal_part
        
        return formatted
    
    def _format_number(self, number):
        """Форматирование числа для отображения: 2 цифры после запятой и разделители тысяч."""
        # Округляем до 2 знаков после запятой
        num_decimal = Decimal(number).quantize(Decimal('0.01'))
        num_str = str(num_decimal)
        
        # Разделяем на целую и дробную части
        parts = num_str.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else '00'
        
        # Обеспечиваем 2 цифры после запятой
        if len(decimal_part) < 2:
            decimal_part = decimal_part.ljust(2, '0')
        
        # Добавляем символ "'" как разделитель тысяч
        formatted = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted = "'" + formatted
            formatted = digit + formatted
        
        formatted += "," + decimal_part
        
        return formatted
    
    def _bind_keyboard(self):
        """Привязка обработчиков клавиатуры."""
        # Цифры 0-9
        for digit in range(10):
            self.root.bind(str(digit), lambda e, d=str(digit): self._number_click(d))
        
        # Операции
        self.root.bind('+', lambda e: self._add())
        self.root.bind('-', lambda e: self._subtract())
        self.root.bind('=', lambda e: self._equals())
        self.root.bind('<Return>', lambda e: self._equals())
        self.root.bind('<KP_Enter>', lambda e: self._equals())  # Enter на цифровой клавиатуре
        
        # Удаление и очистка
        self.root.bind('<BackSpace>', lambda e: self._backspace())
        self.root.bind('<Delete>', lambda e: self._clear_all())
        self.root.bind('c', lambda e: self._clear_all())
        self.root.bind('C', lambda e: self._clear_all())
        
        # Запятая для десятичных чисел
        self.root.bind(',', lambda e: self._number_click('.'))
        self.root.bind('.', lambda e: self._number_click('.'))
        
        # Фокус на главном окне для приёма событий клавиатуры
        self.root.focus_set()
    
    def _create_history_window(self):
        """Создание отдельного окна для ленты вычислений."""
        self.history_window = tk.Toplevel(self.root)
        self.history_window.title("Лента вычислений")
        self.history_window.geometry("300x400")
        self.history_window.resizable(True, True)  # Разрешаем изменение размера
        self.history_window.configure(bg='#C0C0C0')
        self.history_window.transient(self.root)
        
        # Перемещаем окно истории рядом с калькулятором
        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        self.history_window.geometry(f"+{root_x + 330}+{root_y}")
        
        history_label = tk.Label(
            self.history_window, 
            text="История вычислений:",
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            anchor='w'
        )
        history_label.pack(padx=5, pady=(5, 2), fill=tk.X)
        
        # Текстовое поле с прокруткой для истории
        history_scrollbar = tk.Scrollbar(self.history_window)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            self.history_window,
            width=30,
            bg='#FFFFFF',
            fg='#000000',
            font=('Courier', 9),
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=2,
            yscrollcommand=history_scrollbar.set,
            state=tk.DISABLED
        )
        self.history_text.pack(padx=(5, 0), pady=(0, 5), fill=tk.BOTH, expand=True)
        history_scrollbar.config(command=self.history_text.yview)
        
        # Обработчик закрытия окна
        self.history_window.protocol("WM_DELETE_WINDOW", self._toggle_history_window)
    
    def _toggle_history_window(self):
        """Скрытие/показ окна истории."""
        if self.history_window.winfo_viewable():
            self.history_window.withdraw()  # Скрыть окно
        else:
            self.history_window.deiconify()  # Показать окно
            self.history_window.lift()  # Поднять на передний план
    
    def _add_to_history(self, text):
        """Добавление записи в историю."""
        self.history.append(text)
        self._history_append(text + "\n")
    
    def _clear_history(self):
        """Очистка только истории вычислений (ленты)."""
        self.history.clear()
        self._history_clear()

    def _history_append(self, text: str):
        """Добавляет текст в ленту (read-only Text)."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, text)
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def _history_clear(self):
        """Очищает ленту (read-only Text)."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete('1.0', tk.END)
        self.history_text.config(state=tk.DISABLED)

def main():
    """Главная функция для запуска приложения."""
    root = tk.Tk()
    app = OS2Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
