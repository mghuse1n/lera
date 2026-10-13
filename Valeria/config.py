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
FONT_SIZE = 13


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

QPushButton {{
    background-color: {COLOR_ACCENT};
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 6px;
    font-weight: bold;
    min-height: 20px;
}}
QPushButton:hover {{ background-color: #5a9a97; }}
QPushButton:pressed {{ background-color: #4A8582; }}
QPushButton:disabled {{ background-color: #cccccc; color: #666; }}

QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateEdit {{
    background-color: white;
    border: 1px solid #a0d0c0;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QTextEdit:focus, QDateEdit:focus {{
    border: 2px solid {COLOR_ACCENT};
}}

QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background-color: white;
    border: 1px solid {COLOR_ACCENT};
    border-radius: 6px;
    selection-background-color: {COLOR_BG2};
    padding: 4px;
}}

QTableWidget {{
    background-color: white;
    gridline-color: #e5e5e5;
    border: 1px solid #cfcfcf;
    border-radius: 6px;
    alternate-background-color: #fafafa;
    selection-background-color: {COLOR_BG2};
}}
QHeaderView::section {{
    background-color: {COLOR_BG2};
    color: #333;
    padding: 8px 6px;
    border: none;
    border-bottom: 1px solid #a0d0c0;
    font-weight: bold;
}}

QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{
    background: #b8dcd0; border-radius: 5px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLOR_ACCENT}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""


# Стиль для светлых кнопок
STYLE_SECONDARY = f"""
QPushButton {{
    background-color: white;
    color: {COLOR_ACCENT};
    border: 2px solid {COLOR_ACCENT};
    padding: 8px 18px;
    border-radius: 6px;
    font-weight: bold;
}}
QPushButton:hover {{ background-color: {COLOR_BG2}; }}
"""


# Стиль для кнопки удаления
STYLE_DANGER = """
QPushButton {
    background-color: #d9534f;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover { background-color: #c9302c; }
"""


# Стиль для кнопки как ссылка
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