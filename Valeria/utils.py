from datetime import date, timedelta

from db import get_one


SQL_ORDERS_BETWEEN = """
    SELECT COUNT(*) AS cnt
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE oi.product_id = %s AND o.order_date BETWEEN %s AND %s
"""


def discount_for(product_id):
    today = date.today()

    first_current = today.replace(day=1)
    last_previous = first_current - timedelta(days=1)
    first_previous = last_previous.replace(day=1)

    row = get_one(SQL_ORDERS_BETWEEN, (product_id, first_previous, last_previous))

    if row is None:
        return 25

    if row["cnt"] == 0:
        return 25

    return 0


def price_with_discount(price, discount):
    if discount == 0:
        return price

    new_price = price - price * discount / 100
    return round(new_price, 2)