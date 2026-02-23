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
    - Лента вычислений (редактируемая, с пересчётом цепочки)
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
        # Базовое состояние ленты для подсветки изменённых строк (при редактировании)
        self._tape_baseline = []
        
        # Путь к лог-файлу ленты (в папке программы)
        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc.log')
        self._create_widgets()
        self._create_history_window()
        self._load_log()
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
        
        recalc_ribbon_btn = tk.Button(
            ribbon_buttons_frame,
            text="Пересчитать",
            command=self._recalculate_tape,
            bg='#C0C0C0',
            font=('MS Sans Serif', 9),
            relief=tk.RAISED,
            bd=2
        )
        recalc_ribbon_btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
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
            state=tk.NORMAL
        )
        self.history_text.tag_configure('modified', foreground='red')
        self.history_text.bind('<KeyRelease>', self._on_tape_key_release)
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
        """Добавление записи в историю и в файл calc.log."""
        self.history.append(text)
        self._history_append(text + "\n")
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(text + "\n")
        except OSError:
            pass
    
    def _clear_history(self):
        """Очистка истории вычислений (ленты) и содержимого calc.log."""
        self.history.clear()
        self._history_clear()
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                pass
        except OSError:
            pass

    def _history_append(self, text: str):
        """Добавляет текст в ленту (редактируемое поле)."""
        self.history_text.insert(tk.END, text)
        self.history_text.see(tk.END)
        line = text.rstrip('\n')
        if line:
            self._tape_baseline.append(line)

    def _history_clear(self):
        """Очищает ленту и базовое состояние для подсветки."""
        self.history_text.delete('1.0', tk.END)
        self._tape_baseline.clear()

    def _load_log(self):
        """Загрузка ленты из calc.log при запуске."""
        if not os.path.exists(self.log_path):
            return
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n\r')
                    if line:
                        self.history.append(line)
                        self._history_append(line + "\n")
            self._tape_baseline = self.history.copy()
        except OSError:
            pass

    def _on_tape_key_release(self, event=None):
        """Подсветка изменённых строк ленты красным."""
        self._update_tape_modified_marks()

    def _update_tape_modified_marks(self):
        """Помечает красным строки, отличающиеся от базового состояния."""
        self.history_text.tag_remove('modified', '1.0', tk.END)
        current = self.history_text.get('1.0', tk.END)
        lines = [s.rstrip('\r\n') for s in current.split('\n')]
        if lines and lines[-1] == '' and current.endswith('\n'):
            lines.pop()
        for i, line in enumerate(lines):
            if i >= len(self._tape_baseline) or self._tape_baseline[i] != line:
                start = f'{i + 1}.0'
                end = f'{i + 1}.end'
                self.history_text.tag_add('modified', start, end)

    def _parse_display_number(self, s):
        """Преобразует число с ленты (формат 1'234,56) в Decimal. Возвращает None при ошибке."""
        if not s or not s.strip():
            return None
        s = s.strip().replace("'", "").replace(",", ".")
        try:
            return Decimal(s)
        except (InvalidOperation, ValueError):
            return None

    def _parse_tape_line(self, line):
        """
        Парсит строку ленты. Возвращает (left, op, right, result) или (None, None, None, result) для "= C".
        При ошибке возвращает None.
        """
        line = line.strip()
        if not line:
            return None
        if ' = ' not in line:
            return None
        left_side, _, result_str = line.partition(' = ')
        left_side = left_side.strip()
        result_str = result_str.strip()
        result = self._parse_display_number(result_str)
        if result is None:
            return None
        if left_side == '=' or not left_side:
            return (None, None, None, result)
        if ' + ' in left_side:
            parts = left_side.split(' + ', 1)
            if len(parts) != 2:
                return None
            left = self._parse_display_number(parts[0].strip())
            right = self._parse_display_number(parts[1].strip())
            if left is None or right is None:
                return None
            return (left, '+', right, result)
        if ' - ' in left_side:
            parts = left_side.split(' - ', 1)
            if len(parts) != 2:
                return None
            left = self._parse_display_number(parts[0].strip())
            right = self._parse_display_number(parts[1].strip())
            if left is None or right is None:
                return None
            return (left, '-', right, result)
        return None

    def _recalculate_tape(self):
        """
        Пересчёт цепочки вычислений по текущему содержимому ленты.
        Цепочка берётся из виджета (отображает данные из лог-файла), пересчитывается,
        лента и calc.log обновляются.
        """
        content = self.history_text.get('1.0', tk.END)
        lines = [s.strip() for s in content.split('\n') if s.strip()]
        if not lines:
            self._tape_baseline.clear()
            self.history.clear()
            try:
                with open(self.log_path, 'w', encoding='utf-8') as f:
                    pass
            except OSError:
                pass
            self._update_sum_display()
            return
        running_sum = Decimal('0')
        new_lines = []
        for line in lines:
            parsed = self._parse_tape_line(line)
            if parsed is None:
                messagebox.showerror("Ошибка", f"Не удалось разобрать строку: {line}")
                return
            left, op, right, _ = parsed
            if left is None:
                running_sum = _
                new_lines.append("= " + self._format_number(running_sum))
            else:
                # Левый операнд = результат предыдущей строки (цепочка), кроме самой первой строки
                effective_left = running_sum if new_lines else left
                if op == '+':
                    running_sum = effective_left + right
                else:
                    running_sum = effective_left - right
                new_lines.append(
                    f"{self._format_number(effective_left)} {op} {self._format_number(right)} = {self._format_number(running_sum)}"
                )
        new_content = '\n'.join(new_lines) + '\n'
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete('1.0', tk.END)
        self.history_text.insert('1.0', new_content)
        self.history_text.see(tk.END)
        self.history_text.update_idletasks()
        self.history = new_lines.copy()
        self._tape_baseline = new_lines.copy()
        self.current_sum = running_sum
        self._update_sum_display()
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                f.flush()
                if hasattr(os, 'fsync'):
                    os.fsync(f.fileno())
        except (OSError, AttributeError):
            pass

def main():
    """Главная функция для запуска приложения."""
    root = tk.Tk()
    app = OS2Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
