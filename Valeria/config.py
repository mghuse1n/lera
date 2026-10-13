# Файл с настройками. Тут пути, доступ к базе и цвета.

import os


# Пути к папкам проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
PRODUCTS_IMG_DIR = os.path.join(RESOURCES_DIR, 'products')


# Данные для подключения к базе
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'chudo_obuv',
    'user': 'postgres',
    'password': '12345678',
}


# Цвета
COLOR_BG = '#FFFFFF'
COLOR_BG2 = '#D2F6E7'
COLOR_ACCENT = '#70B2AF'
COLOR_LOW_STOCK = '#ff8080'

FONT = 'Calibri'
FONT_SIZE = 14


# Общий стиль для всех окон
STYLESHEET = f"""
QWidget {{
    background-color: {COLOR_BG};
    font-family: '{FONT}';
    font-size: {FONT_SIZE}px;
    color: #333;
}}
QMainWindow, QDialog {{
    background-color: {COLOR_BG};
}}

/* Поля ввода — с фоном и большим скруглением */
QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateEdit {{
    background-color: {COLOR_BG2};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QTextEdit:focus, QDateEdit:focus {{
    background-color: white;
    border: 2px solid {COLOR_ACCENT};
}}

QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: white;
    border: 2px solid {COLOR_ACCENT};
    border-radius: 8px;
    selection-background-color: {COLOR_BG2};
    padding: 4px;
}}

/* Таблицы — только нижние линии, без рамки */
QTableWidget {{
    background-color: white;
    gridline-color: transparent;
    border: none;
    selection-background-color: {COLOR_BG2};
    selection-color: #333;
    alternate-background-color: white;
}}
QTableWidget::item {{
    border-bottom: 1px solid #e0e0e0;
    padding: 6px;
}}
QHeaderView::section {{
    background-color: {COLOR_BG2};
    color: #333;
    padding: 10px 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}

QScrollBar:vertical {{ background: transparent; width: 14px; }}
QScrollBar::handle:vertical {{
    background: {COLOR_ACCENT}; border-radius: 7px; min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{ background: #5a9a97; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}

QLabel {{ color: #333; background-color: transparent; }}
"""


# Обычные кнопки — плоские, с рамкой, белый фон, цветной текст
STYLE_SECONDARY = f"""
QPushButton {{
    background-color: white;
    color: {COLOR_ACCENT};
    border: 2px solid {COLOR_ACCENT};
    padding: 10px 22px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton:hover {{ background-color: {COLOR_BG2}; }}
QPushButton:pressed {{ background-color: #BBEBD7; }}
"""


# Кнопка удаления — плоская, красная рамка, белый фон
STYLE_DANGER = f"""
QPushButton {{
    background-color: white;
    color: #d9534f;
    border: 2px solid #d9534f;
    padding: 10px 22px;
    border-radius: 10px;
    font-weight: bold;
}}
QPushButton:hover {{ background-color: #fdecec; }}
QPushButton:pressed {{ background-color: #f9dcdc; }}
"""


# Кнопка как ссылка — без рамки, подчёркнутая
STYLE_LINK = f"""
QPushButton {{
    background-color: transparent;
    color: {COLOR_ACCENT};
    border: none;
    padding: 4px;
    font-weight: normal;
    text-decoration: underline;
}}
QPushButton:hover {{ color: #4A8582; }}
"""


# Основная акцентная кнопка — залитая, для главных действий
STYLE_PRIMARY = f"""
QPushButton {{
    background-color: {COLOR_ACCENT};
    color: white;
    border: none;
    padding: 10px 22px;
    border-radius: 10px;
    font-weight: bold;
}}
QPushButton:hover {{ background-color: #5a9a97; }}
QPushButton:pressed {{ background-color: #4A8582; }}
QPushButton:disabled {{ background-color: #cccccc; color: #666; }}
"""
