import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


def get_connection():
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    return conn


def get_all(sql, params=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_one(sql, params=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def do_query(sql, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    count = cur.rowcount
    cur.close()
    conn.close()
    return count


def do_insert(sql, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0]
    return None