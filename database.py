
import sqlite3


def create_table():
    connection = sqlite3.connect("invoices.db")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            invoice_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()

    
def create_product_table():
    connection = sqlite3.connect("invoices.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)

    connection.commit()
    connection.close()


create_product_table()


def save_invoice(customer, product, quantity, price, total):
    connection = sqlite3.connect("invoices.db")

    cursor = connection.execute("""
        INSERT INTO invoices
        (customer, product, quantity, price, total, invoice_date)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (customer, product, quantity, price, total))

    invoice_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return invoice_id


def get_invoices():
    connection = sqlite3.connect("invoices.db")
    connection.row_factory = sqlite3.Row

    invoices = connection.execute(
        "SELECT * FROM invoices ORDER BY id DESC"
    ).fetchall()

    connection.close()
    return invoices


create_table()

connection = sqlite3.connect("invoices.db")

columns = [
    row[1] for row in connection.execute(
        "PRAGMA table_info(invoices)"
    ).fetchall()
]

if "invoice_date" not in columns:
    connection.execute(
        "ALTER TABLE invoices ADD COLUMN invoice_date TEXT"
    )
    connection.commit()

connection.close()


def get_summary():
    connection = sqlite3.connect("invoices.db")

    result = connection.execute("""
        SELECT COUNT(*), COALESCE(SUM(total), 0)
        FROM invoices
    """).fetchone()

    connection.close()

    return {
        "invoice_count": result[0],
        "total_sales": result[1]
    }



def delete_invoice(invoice_id):
    connection = sqlite3.connect("invoices.db")
    connection.execute(
        "DELETE FROM invoices WHERE id = ?",
        (invoice_id,)
    )
    connection.commit()
    connection.close()


def search_invoices(customer_name):
    connection = sqlite3.connect("invoices.db")
    connection.row_factory = sqlite3.Row

    invoices = connection.execute("""
        SELECT * FROM invoices
        WHERE customer LIKE ?
        ORDER BY id DESC
    """, (f"%{customer_name}%",)).fetchall()

    connection.close()
    return invoices


def get_invoice_items(invoice_id):
    connection = sqlite3.connect("invoices.db")
    connection.row_factory = sqlite3.Row

    items = connection.execute("""
        SELECT product, quantity, price, subtotal
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,)).fetchall()

    connection.close()
    return items
