import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QScrollArea, QSpinBox,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox,
)

from config import (
    COLOR_BG2, COLOR_LOW_STOCK, PRODUCTS_IMG_DIR, RESOURCES_DIR,
    STYLESHEET, STYLE_SECONDARY,
)
from db import get_all, get_one
from utils import discount_for, price_with_discount


SQL_PRODUCTS = """
    SELECT p.*, COALESCE(SUM(si.quantity_available), 0) AS total_quantity
    FROM products p
    LEFT JOIN stock_items si ON si.product_id = p.id
    GROUP BY p.id
    ORDER BY p.name
"""

SQL_PRODUCT = "SELECT * FROM products WHERE id = %s"

SQL_SIZES = """
    SELECT s.id AS size_id, s.value, si.quantity_available
    FROM stock_items si
    JOIN sizes s ON s.id = si.size_id
    WHERE si.product_id = %s AND si.quantity_available > 0
    ORDER BY s.value
"""


class ProductCard(QFrame):

    clicked = pyqtSignal(int)

    def __init__(self, product, discount, parent=None):
        super().__init__(parent)
        self.product_id = product["id"]
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        image = QLabel()
        image.setFixedHeight(200)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setPixmap(self.load_image(product.get("image_path")))
        layout.addWidget(image)

        name = QLabel(product.get("manufacturer", "") + " | " + product.get("name", ""))
        name.setStyleSheet("font-size: 15px; font-weight: bold;")
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        cat = QLabel("Категория: " + product.get("category", ""))
        cat.setStyleSheet("font-size: 12px; color: #666;")
        cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cat)

        qty = int(product.get("total_quantity", 0))
        qty_label = QLabel("В наличии: " + str(qty))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if qty <= 3:
            qty_label.setStyleSheet("color: " + COLOR_LOW_STOCK + "; font-weight: bold;")
        layout.addWidget(qty_label)

        base = float(product["price"])
        final = price_with_discount(base, discount)

        if discount > 0:
            price_text = (
                "<span style='color:#999;text-decoration:line-through;font-size:12px;'>"
                + str(round(base, 2)) + " ₽</span><br>"
                "<span style='color:#70B2AF;font-size:20px;font-weight:bold;'>"
                + str(round(final, 2)) + " ₽</span>"
            )
        else:
            price_text = (
                "<span style='color:#70B2AF;font-size:20px;font-weight:bold;'>"
                + str(round(final, 2)) + " ₽</span>"
            )

        price = QLabel(price_text)
        price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price)

        layout.addSpacing(5)

        open_btn = QPushButton("Открыть")
        open_btn.clicked.connect(self.on_open_click)
        layout.addWidget(open_btn)

        if qty <= 3:
            self.setStyleSheet("""
                ProductCard {
                    border: 2px solid #ff8080;
                    border-radius: 10px;
                    background-color: rgba(255, 128, 128, 30);
                }
            """)
        else:
            self.setStyleSheet("""
                ProductCard {
                    border: 1px solid #e0e0e0;
                    border-radius: 10px;
                    background-color: white;
                }
            """)

    def load_image(self, name):
        size_w = 330
        size_h = 200
        if name:
            path = os.path.join(PRODUCTS_IMG_DIR, name)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                pixmap = pixmap.scaled(
                    size_w, size_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                return pixmap
        stub = os.path.join(RESOURCES_DIR, "picture.png")
        if os.path.exists(stub):
            pixmap = QPixmap(stub)
            pixmap = pixmap.scaled(
                size_w, size_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            return pixmap
        return QPixmap()

    def on_open_click(self):
        self.clicked.emit(self.product_id)


class ProductWindow(QDialog):

    def __init__(self, product_id, cart, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.cart = cart

        self.setWindowTitle("Чудо Обувь - Товар")
        self.resize(600, 780)
        self.setStyleSheet(STYLESHEET)

        self.product = get_one(SQL_PRODUCT, (product_id,))

        if self.product is None:
            QMessageBox.critical(self, "Ошибка", "Товар не найден")
            self.reject()
            return

        self.product = dict(self.product)
        self.sizes = get_all(SQL_SIZES, (product_id,))
        self.discount = discount_for(product_id)

        self.make_interface()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title = QLabel("Просмотр товара")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        image = QLabel()
        image.setFixedHeight(260)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setPixmap(self.load_image())
        main_layout.addWidget(image)

        name_text = self.product.get("manufacturer", "") + " | " + self.product.get("name", "")
        name = QLabel(name_text)
        name.setStyleSheet("font-size: 17px; font-weight: bold;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        main_layout.addWidget(name)

        cat = QLabel("Категория: " + self.product.get("category", ""))
        cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(cat)

        comp = QLabel("Состав: " + self.product.get("composition", ""))
        comp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        comp.setWordWrap(True)
        main_layout.addWidget(comp)

        desc = QTextEdit(self.product.get("description") or "")
        desc.setReadOnly(True)
        desc.setMaximumHeight(80)
        main_layout.addWidget(desc)

        base = float(self.product["price"])
        final = price_with_discount(base, self.discount)

        if self.discount > 0:
            price_text = "<b>Цена со скидкой: " + str(round(final, 2)) + " ₽</b>"
            price_text = price_text + " <span style='color:#999;text-decoration:line-through;'>"
            price_text = price_text + str(round(base, 2)) + " ₽</span>"
        else:
            price_text = "<b>Цена: " + str(round(base, 2)) + " ₽</b>"

        price_label = QLabel(price_text)
        price_label.setStyleSheet("font-size: 16px;")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(price_label)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Размер:"))

        self.size_combo = QComboBox()
        if len(self.sizes) == 0:
            self.size_combo.addItem("Нет в наличии", None)
            self.size_combo.setEnabled(False)
        else:
            for size in self.sizes:
                text = str(size["value"]) + " (доступно: " + str(size["quantity_available"]) + ")"
                self.size_combo.addItem(text, (size["size_id"], size["quantity_available"]))
        size_row.addWidget(self.size_combo, 1)

        size_row.addWidget(QLabel("Кол-во:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(1)
        size_row.addWidget(self.qty_spin)

        self.size_combo.currentIndexChanged.connect(self.on_size_changed)
        self.on_size_changed()
        main_layout.addLayout(size_row)

        main_layout.addStretch()

        buttons = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.on_add_click)
        if len(self.sizes) == 0:
            self.add_btn.setEnabled(False)
        buttons.addWidget(self.add_btn)

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet(STYLE_SECONDARY)
        back_btn.clicked.connect(self.reject)
        buttons.addWidget(back_btn)

        main_layout.addLayout(buttons)
        self.setLayout(main_layout)

    def load_image(self):
        name = self.product.get("image_path")
        if name:
            path = os.path.join(PRODUCTS_IMG_DIR, name)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                pixmap = pixmap.scaled(
                    500, 260,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                return pixmap
        stub = os.path.join(RESOURCES_DIR, "picture.png")
        if os.path.exists(stub):
            pixmap = QPixmap(stub)
            pixmap = pixmap.scaled(
                500, 260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            return pixmap
        return QPixmap()

    def on_size_changed(self):
        data = self.size_combo.currentData()
        if data:
            max_qty = data[1]
        else:
            max_qty = 0
        self.qty_spin.setMaximum(max(max_qty, 1))

    def on_add_click(self):
        data = self.size_combo.currentData()

        if data is None:
            QMessageBox.critical(self, "Ошибка", "Выберите размер")
            return

        size_id = data[0]
        available = data[1]
        qty = self.qty_spin.value()

        if qty <= 0 or qty > available:
            QMessageBox.critical(self, "Ошибка", "Количество от 1 до " + str(available))
            return

        final_price = price_with_discount(float(self.product["price"]), self.discount)
        size_text = self.size_combo.currentText().split(" ")[0]

        found = False
        for item in self.cart:
            if item["product_id"] == self.product_id and item["size_id"] == size_id:
                item["quantity"] = item["quantity"] + qty
                found = True

        if found:
            QMessageBox.information(self, "Готово", "Количество увеличено")
            self.accept()
            return

        self.cart.append({
            "product_id": self.product_id,
            "name": self.product["name"],
            "manufacturer": self.product.get("manufacturer", ""),
            "size_id": size_id,
            "size_value": size_text,
            "quantity": qty,
            "price": final_price,
        })

        QMessageBox.information(self, "Готово", "Товар добавлен")
        self.accept()


class ShopWindow(QMainWindow):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = []

        self.setWindowTitle("Чудо Обувь - Каталог")
        self.resize(1100, 800)
        self.setStyleSheet(STYLESHEET)

        icon_path = os.path.join(RESOURCES_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.make_interface()
        self.load_products()

    def make_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.make_title())
        main_layout.addWidget(self.make_top_bar())
        main_layout.addWidget(self.make_scroll(), 1)

    def make_title(self):
        wrapper = QWidget()
        wrapper.setStyleSheet("background-color: white;")

        row = QHBoxLayout(wrapper)
        row.setContentsMargins(15, 10, 15, 10)

        title = QLabel("Каталог товаров")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #70B2AF;")
        row.addWidget(title)
        row.addStretch()

        return wrapper

    def make_top_bar(self):
        bar = QWidget()
        bar.setStyleSheet("background-color: " + COLOR_BG2 + ";")

        row = QHBoxLayout(bar)
        row.setContentsMargins(15, 10, 15, 10)
        row.setSpacing(10)

        logo_path = os.path.join(RESOURCES_DIR, "logo.png")
        if os.path.exists(logo_path):
            logo = QLabel()
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaledToHeight(50)
            logo.setPixmap(pixmap)
            row.addWidget(logo)

        if self.user is not None:
            row.addWidget(QLabel("Поиск:"))
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск...")
            self.search_input.textChanged.connect(self.refresh_products)
            row.addWidget(self.search_input, 2)

            row.addWidget(QLabel("Категория:"))
            self.category_combo = QComboBox()
            self.category_combo.addItem("Все", None)
            self.category_combo.currentIndexChanged.connect(self.refresh_products)
            row.addWidget(self.category_combo, 1)

        row.addStretch()

        if self.user is not None:
            fio = QLabel(self.user.get("full_name", ""))
            fio.setStyleSheet("font-weight: bold;")
            row.addWidget(fio)

        if self.is_logged_in():
            self.cart_btn = QPushButton("Корзина")
            self.cart_btn.clicked.connect(self.on_cart_click)
            row.addWidget(self.cart_btn)

        if self.is_staff():
            orders_btn = QPushButton("Заказы")
            orders_btn.clicked.connect(self.on_orders_click)
            row.addWidget(orders_btn)

        if self.user is not None:
            logout_btn = QPushButton("Выйти")
            logout_btn.setStyleSheet(STYLE_SECONDARY)
            logout_btn.clicked.connect(self.on_logout_click)
            row.addWidget(logout_btn)

        return bar

    def make_scroll(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.cards_grid = QGridLayout(container)
        self.cards_grid.setSpacing(15)
        self.cards_grid.setContentsMargins(15, 15, 15, 15)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(container)

        return scroll

    def is_logged_in(self):
        if self.user and self.user.get("id"):
            return True
        return False

    def is_staff(self):
        if self.user and self.user.get("role_name") in ("Администратор", "Менеджер"):
            return True
        return False

    def load_products(self):
        rows = get_all(SQL_PRODUCTS)
        self.all_products = []
        for r in rows:
            self.all_products.append(dict(r))

        if self.user is not None:
            self.fill_categories()

        self.refresh_products()

    def fill_categories(self):
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("Все", None)

        categories = set()
        for p in self.all_products:
            categories.add(p["category"])

        for cat in sorted(categories):
            self.category_combo.addItem(cat, cat)

        self.category_combo.blockSignals(False)

    def refresh_products(self):
        products = []
        for p in self.all_products:
            products.append(p)

        if self.user is not None:
            cat = self.category_combo.currentData()
            if cat:
                filtered = []
                for p in products:
                    if p["category"] == cat:
                        filtered.append(p)
                products = filtered

            query = self.search_input.text().strip().lower()
            if query != "":
                filtered = []
                for p in products:
                    name_low = p["name"].lower()
                    desc_low = (p.get("description") or "").lower()
                    if query in name_low or query in desc_low:
                        filtered.append(p)
                products = filtered

        self.show_cards(products)

    def show_cards(self, products):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if len(products) == 0:
            self.cards_grid.addWidget(QLabel("Товары не найдены"), 0, 0)
            return

        columns = 2
        i = 0
        for product in products:
            discount = discount_for(product["id"])
            card = ProductCard(product, discount)
            card.clicked.connect(self.on_product_click)
            row = i // columns
            col = i % columns
            self.cards_grid.addWidget(card, row, col)
            i = i + 1

    def on_product_click(self, product_id):
        if not self.is_logged_in():
            QMessageBox.information(self, "Информация", "Для заказа нужно войти")
            return

        dialog = ProductWindow(product_id, self.cart, parent=self)
        if dialog.exec():
            self.refresh_cart_button()

    def on_cart_click(self):
        from orders import CartWindow
        dialog = CartWindow(self.user, self.cart, parent=self)
        if dialog.exec():
            self.load_products()
            self.refresh_cart_button()

    def on_orders_click(self):
        from orders import OrdersWindow
        dialog = OrdersWindow(self.user, parent=self)
        dialog.exec()
        self.load_products()

    def on_logout_click(self):
        self.close()

        from login import LoginWindow
        login = LoginWindow()
        if not login.exec():
            return

        self.new_window = ShopWindow(user=login.user)
        self.new_window.show()

    def refresh_cart_button(self):
        if not hasattr(self, "cart_btn"):
            return
        if len(self.cart) > 0:
            total = 0
            for item in self.cart:
                total = total + item["quantity"]
            self.cart_btn.setText("Корзина (" + str(total) + ")")
        else:
            self.cart_btn.setText("Корзина")
