import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox,
)

from config import STYLESHEET, STYLE_LINK, RESOURCES_DIR
from db import get_one


SQL_FIND_USER = """
    SELECT u.id, u.last_name, u.first_name, u.middle_name,
           u.login, r.name AS role_name
    FROM users u
    JOIN roles r ON r.id = u.role_id
    WHERE u.login = %s
"""


class LoginWindow(QDialog):

    def __init__(self):
        super().__init__()

        self.user = None

        self.setWindowTitle("Чудо Обувь - Вход")
        self.resize(520, 560)
        self.setStyleSheet(STYLESHEET)

        icon_path = os.path.join(RESOURCES_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.make_interface()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(12)

        logo_path = os.path.join(RESOURCES_DIR, "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaledToHeight(140)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(logo_label)

        main_layout.addSpacing(10)

        title = QLabel("Вход в систему")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #70B2AF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        main_layout.addSpacing(20)
        main_layout.addWidget(QLabel("Логин:"))

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        main_layout.addWidget(self.login_input)

        main_layout.addSpacing(15)

        login_button = QPushButton("Войти")
        login_button.setMinimumHeight(45)
        login_button.clicked.connect(self.on_login_click)
        main_layout.addWidget(login_button)

        main_layout.addSpacing(5)

        guest_button = QPushButton("Продолжить как гость")
        guest_button.setStyleSheet(STYLE_LINK)
        guest_button.setCursor(Qt.CursorShape.PointingHandCursor)
        guest_button.clicked.connect(self.on_guest_click)
        main_layout.addWidget(guest_button)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def on_login_click(self):
        login = self.login_input.text().strip()

        if login == "":
            QMessageBox.critical(self, "Ошибка", "Введите логин")
            return

        row = get_one(SQL_FIND_USER, (login,))

        if row is None:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
            return

        fio = ""
        if row["last_name"]:
            fio = fio + row["last_name"]
        if row["first_name"]:
            fio = fio + " " + row["first_name"]
        if row["middle_name"]:
            fio = fio + " " + row["middle_name"]

        self.user = {
            "id": row["id"],
            "login": row["login"],
            "role_name": row["role_name"],
            "full_name": fio,
        }

        self.accept()

    def on_guest_click(self):
        self.user = {
            "id": None,
            "login": None,
            "role_name": "Неавторизованный",
            "full_name": "Гость",
        }
        self.accept()