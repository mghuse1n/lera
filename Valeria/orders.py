from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QMessageBox,
)

from config import STYLESHEET, STYLE_DANGER, STYLE_SECONDARY
from db import get_all, get_one, do_query, do_insert
from utils import discount_for, price_with_discount


SQL_INSERT_ORDER = """
    INSERT INTO orders (order_date, user_id, client_name)
    VALUES (CURRENT_DATE, %s, %s)
    RETURNING id
"""

SQL_DECREASE_STOCK = """
    UPDATE stock_items
    SET quantity_available = quantity_available - %s
    WHERE product_id = %s AND size_id = %s AND quantity_available >= %s
"""

SQL_INSERT_ITEM = """
    INSERT INTO order_items
        (order_id, product_id, size_id, quantity, price_at_moment)
    VALUES (%s, %s, %s, %s, %s)
"""

SQL_LOAD_ORDERS = """
    SELECT o.id, o.order_date, o.client_name,
           COALESCE(SUM(oi.quantity * oi.price_at_moment), 0) AS total
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id
    ORDER BY o.order_date DESC, o.id DESC
"""

SQL_DELETE_ORDER = "DELETE FROM orders WHERE id = %s"

SQL_ORDER = "SELECT * FROM orders WHERE id = %s"

SQL_ORDER_ITEMS = """
    SELECT oi.id, p.name AS product_name, p.manufacturer,
           s.value AS size_value, oi.quantity, oi.price_at_moment,
           (oi.quantity * oi.price_at_moment) AS subtotal
    FROM order_items oi
    JOIN products p ON p.id = oi.product_id
    JOIN sizes s ON s.id = oi.size_id
    WHERE oi.order_id = %s
    ORDER BY oi.id
"""

SQL_UPDATE_DATE = "UPDATE orders SET order_date = %s WHERE id = %s"
SQL_DELETE_ITEM = "DELETE FROM order_items WHERE id = %s"

SQL_PRODUCTS = "SELECT id, name, manufacturer, price FROM products ORDER BY name"

SQL_SIZES = """
    SELECT s.id AS size_id, s.value, si.quantity_available
    FROM stock_items si
    JOIN sizes s ON s.id = si.size_id
    WHERE si.product_id = %s AND si.quantity_available > 0
    ORDER BY s.value
"""


class CartWindow(QDialog):

    def __init__(self, user, cart, parent=None):
        super().__init__(parent)
        self.user = user
        self.cart = cart

        self.setWindowTitle("Чудо Обувь - Корзина")
        self.resize(820, 560)
        self.setStyleSheet(STYLESHEET)

        self.make_interface()
        self.reload_table()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Корзина и оформление заказа")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
        main_layout.addWidget(title)

        top = QHBoxLayout()

        remove_btn = QPushButton("Удалить позицию")
        remove_btn.setStyleSheet(STYLE_SECONDARY)
        remove_btn.clicked.connect(self.on_remove_click)
        top.addWidget(remove_btn)

        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet(STYLE_SECONDARY)
        clear_btn.clicked.connect(self.on_clear_click)
        top.addWidget(clear_btn)

        top.addStretch()
        main_layout.addLayout(top)

        self.table = QTableWidget()
        headers = ["ID", "Наименование", "Производитель", "Размер", "Кол-во", "Сумма"]
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table, 1)

        self.total_label = QLabel("Итого: 0.00 руб.")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #70B2AF;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.total_label)

        bottom = QHBoxLayout()
        bottom.addStretch()

        checkout_btn = QPushButton("Оформить заказ")
        checkout_btn.clicked.connect(self.on_checkout_click)
        bottom.addWidget(checkout_btn)

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet(STYLE_SECONDARY)
        back_btn.clicked.connect(self.reject)
        bottom.addWidget(back_btn)

        main_layout.addLayout(bottom)
        self.setLayout(main_layout)

    def reload_table(self):
        self.table.setRowCount(0)
        total = 0.0

        i = 0
        for item in self.cart:
            subtotal = item["price"] * item["quantity"]
            total = total + subtotal
            self.table.insertRow(i)

            self.table.setItem(i, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(i, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(item.get("manufacturer", "")))
            self.table.setItem(i, 3, QTableWidgetItem(str(item["size_value"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(round(subtotal, 2))))

            i = i + 1

        self.total_label.setText("Итого: " + str(round(total, 2)) + " руб.")

    def on_remove_click(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите строку")
            return
        self.cart.pop(row)
        self.reload_table()

    def on_clear_click(self):
        if len(self.cart) == 0:
            return
        reply = QMessageBox.question(self, "Вопрос", "Очистить корзину?")
        if reply == QMessageBox.StandardButton.Yes:
            self.cart.clear()
            self.reload_table()

    def on_checkout_click(self):
        if len(self.cart) == 0:
            QMessageBox.critical(self, "Ошибка", "Корзина пуста")
            return

        if not self.user or not self.user.get("id"):
            QMessageBox.critical(self, "Ошибка", "Нужна авторизация")
            return

        reply = QMessageBox.question(self, "Вопрос", "Оформить заказ?")
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            order_id = do_insert(
                SQL_INSERT_ORDER,
                (self.user["id"], self.user["full_name"])
            )

            for item in self.cart:
                count = do_query(SQL_DECREASE_STOCK, (
                    item["quantity"],
                    item["product_id"],
                    item["size_id"],
                    item["quantity"],
                ))

                if count == 0:
                    QMessageBox.critical(self, "Ошибка", "Не хватает товара")
                    return

                do_query(SQL_INSERT_ITEM, (
                    order_id,
                    item["product_id"],
                    item["size_id"],
                    item["quantity"],
                    item["price"],
                ))

            QMessageBox.information(self, "Готово", "Заказ оформлен")
            self.cart.clear()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class OrdersWindow(QDialog):

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.orders = []

        self.setWindowTitle("Чудо Обувь - Заказы")
        self.resize(860, 580)
        self.setStyleSheet(STYLESHEET)

        self.make_interface()
        self.reload_table()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()

        title = QLabel("Список заказов")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
        header.addWidget(title)
        header.addStretch()

        create_btn = QPushButton("+ Создать заказ")
        create_btn.clicked.connect(self.on_create_click)
        header.addWidget(create_btn)

        main_layout.addLayout(header)

        self.table = QTableWidget()
        headers = ["Номер", "Дата", "Клиент", "Сумма"]
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.on_open_click)
        main_layout.addWidget(self.table, 1)

        bottom = QHBoxLayout()

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet(STYLE_SECONDARY)
        back_btn.clicked.connect(self.reject)
        bottom.addWidget(back_btn)

        bottom.addStretch()

        open_btn = QPushButton("Открыть заказ")
        open_btn.clicked.connect(self.on_open_click)
        bottom.addWidget(open_btn)

        delete_btn = QPushButton("Удалить заказ")
        delete_btn.setStyleSheet(STYLE_DANGER)
        delete_btn.clicked.connect(self.on_delete_click)
        bottom.addWidget(delete_btn)

        main_layout.addLayout(bottom)
        self.setLayout(main_layout)

    def reload_table(self):
        rows = get_all(SQL_LOAD_ORDERS)
        self.orders = []
        for r in rows:
            self.orders.append(dict(r))

        self.table.setRowCount(0)

        i = 0
        for order in self.orders:
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(order["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(order["order_date"])))
            self.table.setItem(i, 2, QTableWidgetItem(order["client_name"]))
            self.table.setItem(i, 3, QTableWidgetItem(str(round(float(order["total"]), 2))))
            i = i + 1

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.orders[row]["id"]

    def on_open_click(self):
        order_id = self.get_selected_id()
        if order_id is None:
            QMessageBox.critical(self, "Ошибка", "Выберите заказ")
            return

        dialog = OrderDetailWindow(order_id, self.user, parent=self)
        dialog.exec()
        self.reload_table()

    def on_create_click(self):
        dialog = NewOrderWindow(self.user, parent=self)
        if dialog.exec():
            self.reload_table()

    def on_delete_click(self):
        order_id = self.get_selected_id()
        if order_id is None:
            QMessageBox.critical(self, "Ошибка", "Выберите заказ")
            return

        reply = QMessageBox.question(self, "Вопрос", "Удалить заказ?")
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            do_query(SQL_DELETE_ORDER, (order_id,))
            QMessageBox.information(self, "Готово", "Заказ удалён")
            self.reload_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class OrderDetailWindow(QDialog):

    def __init__(self, order_id, user, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.user = user
        self.is_admin = user.get("role_name") == "Администратор"
        self.items = []

        self.setWindowTitle("Чудо Обувь - Заказ")
        self.resize(880, 560)
        self.setStyleSheet(STYLESHEET)

        self.make_interface()
        self.reload_data()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()

        self.header_label = QLabel("Заказ")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
        header.addWidget(self.header_label)
        header.addStretch()

        self.client_label = QLabel("")
        header.addWidget(self.client_label)

        main_layout.addLayout(header)

        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Дата:"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.is_admin:
            self.date_edit.setEnabled(True)
        else:
            self.date_edit.setEnabled(False)
        date_row.addWidget(self.date_edit)
        date_row.addStretch()
        main_layout.addLayout(date_row)

        self.table = QTableWidget()
        headers = ["ID", "Модель", "Производитель", "Размер", "Кол-во", "Сумма"]
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table, 1)

        self.total_label = QLabel("Итого: 0.00 руб.")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #70B2AF;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.total_label)

        bottom = QHBoxLayout()

        if self.is_admin:
            save_btn = QPushButton("Сохранить изменения")
            save_btn.clicked.connect(self.on_save_click)
            bottom.addWidget(save_btn)

            delete_btn = QPushButton("Удалить позицию")
            delete_btn.setStyleSheet(STYLE_DANGER)
            delete_btn.clicked.connect(self.on_delete_item_click)
            bottom.addWidget(delete_btn)

        bottom.addStretch()

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet(STYLE_SECONDARY)
        back_btn.clicked.connect(self.accept)
        bottom.addWidget(back_btn)

        main_layout.addLayout(bottom)
        self.setLayout(main_layout)

    def reload_data(self):
        order = get_one(SQL_ORDER, (self.order_id,))
        if order is None:
            QMessageBox.critical(self, "Ошибка", "Заказ не найден")
            self.reject()
            return

        d = order["order_date"]
        self.date_edit.setDate(QDate(d.year, d.month, d.day))

        self.header_label.setText("Заказ №" + str(self.order_id))
        self.client_label.setText("Клиент: " + order["client_name"])

        rows = get_all(SQL_ORDER_ITEMS, (self.order_id,))
        self.items = []
        for r in rows:
            self.items.append(dict(r))

        self.table.setRowCount(0)
        total = 0.0

        i = 0
        for item in self.items:
            subtotal = float(item["subtotal"])
            total = total + subtotal

            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(item["manufacturer"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(str(item["size_value"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(round(subtotal, 2))))
            i = i + 1

        self.total_label.setText("Итого: " + str(round(total, 2)) + " руб.")

    def on_save_click(self):
        if not self.is_admin:
            return

        new_date = self.date_edit.date().toPyDate()

        try:
            do_query(SQL_UPDATE_DATE, (new_date, self.order_id))
            QMessageBox.information(self, "Готово", "Дата сохранена")
            self.reload_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def on_delete_item_click(self):
        if not self.is_admin:
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.critical(self, "Ошибка", "Выберите позицию")
            return

        item_id = self.items[row]["id"]

        reply = QMessageBox.question(self, "Вопрос", "Удалить позицию?")
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            do_query(SQL_DELETE_ITEM, (item_id,))
            QMessageBox.information(self, "Готово", "Позиция удалена")
            self.reload_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class NewOrderWindow(QDialog):

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.cart = []
        self.all_products = []

        self.setWindowTitle("Чудо Обувь - Новый заказ")
        self.resize(1100, 650)
        self.setStyleSheet(STYLESHEET)

        self.make_interface()
        self.load_products()

    def make_interface(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Создание нового заказа")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
        main_layout.addWidget(title)

        main_row = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Каталог:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название...")
        self.search_input.textChanged.connect(self.filter_products)
        left.addWidget(self.search_input)

        self.products_list = QListWidget()
        self.products_list.itemDoubleClicked.connect(self.on_add_click)
        left.addWidget(self.products_list, 1)
        main_row.addLayout(left, 1)

        center = QVBoxLayout()
        center.setSpacing(15)
        center.addStretch()

        add_btn = QPushButton("->")
        add_btn.setFixedSize(55, 55)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF; color: white;
                border: none; border-radius: 27px;
                font-size: 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5a9a97; }
        """)
        add_btn.clicked.connect(self.on_add_click)
        center.addWidget(add_btn)

        remove_btn = QPushButton("<-")
        remove_btn.setFixedSize(55, 55)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: #70B2AF;
                border: 2px solid #70B2AF; border-radius: 27px;
                font-size: 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #D2F6E7; }
        """)
        remove_btn.clicked.connect(self.on_remove_click)
        center.addWidget(remove_btn)
        center.addStretch()
        main_row.addLayout(center)

        right = QVBoxLayout()

        client_row = QHBoxLayout()
        client_row.addWidget(QLabel("Клиент:"))
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Иванов Иван Иванович")
        client_row.addWidget(self.client_input, 1)
        right.addLayout(client_row)

        right.addWidget(QLabel("Позиции:"))

        self.cart_table = QTableWidget()
        headers = ["Наименование", "Размер", "Кол-во", "Цена", "Сумма"]
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(headers)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right.addWidget(self.cart_table, 1)

        self.total_label = QLabel("Итого: 0.00 руб.")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #70B2AF;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self.total_label)

        main_row.addLayout(right, 1)
        main_layout.addLayout(main_row, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()

        save_btn = QPushButton("Сохранить заказ")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.on_save_click)
        bottom.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet(STYLE_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        bottom.addWidget(cancel_btn)

        main_layout.addLayout(bottom)
        self.setLayout(main_layout)

    def load_products(self):
        rows = get_all(SQL_PRODUCTS)
        self.all_products = []
        for r in rows:
            self.all_products.append(dict(r))
        self.filter_products()

    def filter_products(self):
        query = self.search_input.text().strip().lower()
        self.products_list.clear()

        for product in self.all_products:
            if query != "" and query not in product["name"].lower():
                continue

            text = product["manufacturer"] + " | " + product["name"]
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, product)
            self.products_list.addItem(item)

    def reload_cart(self):
        self.cart_table.setRowCount(0)
        total = 0.0

        i = 0
        for item in self.cart:
            subtotal = item["price"] * item["quantity"]
            total = total + subtotal

            self.cart_table.insertRow(i)
            self.cart_table.setItem(i, 0, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(i, 1, QTableWidgetItem(str(item["size_value"])))
            self.cart_table.setItem(i, 2, QTableWidgetItem(str(item["quantity"])))
            self.cart_table.setItem(i, 3, QTableWidgetItem(str(round(item["price"], 2))))
            self.cart_table.setItem(i, 4, QTableWidgetItem(str(round(subtotal, 2))))
            i = i + 1

        self.total_label.setText("Итого: " + str(round(total, 2)) + " руб.")

    def on_add_click(self):
        current = self.products_list.currentItem()
        if current is None:
            QMessageBox.critical(self, "Ошибка", "Выберите товар")
            return

        product = current.data(Qt.ItemDataRole.UserRole)
        sizes = get_all(SQL_SIZES, (product["id"],))

        if len(sizes) == 0:
            QMessageBox.critical(self, "Ошибка", "Нет в наличии")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор размера")
        dialog.setStyleSheet(STYLESHEET)
        form = QFormLayout(dialog)

        size_combo = QComboBox()
        for s in sizes:
            text = str(s["value"]) + " (доступно: " + str(s["quantity_available"]) + ")"
            size_combo.addItem(text, (s["size_id"], s["quantity_available"], s["value"]))
        form.addRow("Размер:", size_combo)

        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(sizes[0]["quantity_available"])
        form.addRow("Количество:", qty_spin)

        def sync_max():
            data = size_combo.currentData()
            if data:
                qty_spin.setMaximum(data[1])
        size_combo.currentIndexChanged.connect(sync_max)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if not dialog.exec():
            return

        data = size_combo.currentData()
        size_id = data[0]
        available = data[1]
        size_value = data[2]
        qty = qty_spin.value()

        if qty <= 0 or qty > available:
            QMessageBox.critical(self, "Ошибка", "Неверное количество")
            return

        price = price_with_discount(float(product["price"]), discount_for(product["id"]))

        self.cart.append({
            "product_id": product["id"],
            "name": product["name"],
            "size_id": size_id,
            "size_value": size_value,
            "quantity": qty,
            "price": price,
        })
        self.reload_cart()

    def on_remove_click(self):
        row = self.cart_table.currentRow()
        if row < 0:
            QMessageBox.critical(self, "Ошибка", "Выберите позицию")
            return
        self.cart.pop(row)
        self.reload_cart()

    def on_save_click(self):
        client = self.client_input.text().strip()

        if client == "":
            QMessageBox.critical(self, "Ошибка", "Введите ФИО клиента")
            return

        if len(self.cart) == 0:
            QMessageBox.critical(self, "Ошибка", "Добавьте товары")
            return

        reply = QMessageBox.question(self, "Вопрос", "Сохранить заказ?")
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            order_id = do_insert(SQL_INSERT_ORDER, (self.user["id"], client))

            for item in self.cart:
                count = do_query(SQL_DECREASE_STOCK, (
                    item["quantity"],
                    item["product_id"],
                    item["size_id"],
                    item["quantity"],
                ))

                if count == 0:
                    QMessageBox.critical(self, "Ошибка", "Не хватает товара")
                    return

                do_query(SQL_INSERT_ITEM, (
                    order_id,
                    item["product_id"],
                    item["size_id"],
                    item["quantity"],
                    item["price"],
                ))

            QMessageBox.information(self, "Готово", "Заказ создан")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))