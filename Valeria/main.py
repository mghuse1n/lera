import sys

from PyQt6.QtWidgets import QApplication

from config import STYLESHEET
from login import LoginWindow
from shop import ShopWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    login = LoginWindow()

    if not login.exec():
        sys.exit(0)

    window = ShopWindow(user=login.user)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()