from decimal import Decimal

import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    "host": 'localhost', # put your credentials here
    "port": "5432", # put your credentials here
    "dbname": "stores", # put your credentials here
    "user": "postgres", # put your credentials here
    "password": "1", # put your credentials here
}


CUSTOMERS = [
    ("John Smith", "john.smith@example.com", Decimal("150.00")),
    ("Anna Brown", "anna.brown@example.com", Decimal("300.00")),
    ("Michael Johnson", "michael.johnson@example.com", Decimal("75.50")),
    ("Kate Wilson", "kate.wilson@example.com", Decimal("500.00")),
]

PRODUCTS = [
    ("Laptop", Decimal("1200.00"), 10),
    ("Mouse", Decimal("25.00"), 100),
    ("Keyboard", Decimal("70.00"), 50),
    ("Monitor", Decimal("250.00"), 20),
    ("USB-C Cable", Decimal("15.00"), 200),
]

ORDERS = [
    (1, Decimal("0.00")),
    (2, Decimal("0.00")),
    (3, Decimal("0.00")),
]


ORDER_ITEMS = [
    (1, 1, 1, Decimal("1200.00")),
    (1, 2, 2, Decimal("25.00")),
    (2, 3, 1, Decimal("70.00")),
    (2, 5, 3, Decimal("15.00")),
    (3, 4, 2, Decimal("250.00")),
]


def table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        """
        select exists (
            select 1
            from information_schema.tables
            where table_schema = 'public'
              and table_name = %s
        );
        """,
        (table_name,),
    )
    return cursor.fetchone()[0]


def validate_schema(cursor) -> None:
    required_tables = ["customers", "products", "orders", "order_items", "order_log"]
    missing_tables = [table for table in required_tables if not table_exists(cursor, table)]

    if missing_tables:
        raise RuntimeError(
            "Missing tables: "
            + ", ".join(missing_tables)
            + ". Create the schema before running this script."
        )


def clear_tables(cursor) -> None:
    cursor.execute(
        """
        truncate table
            order_log,
            order_items,
            orders,
            products,
            customers
        restart identity cascade;
        """
    )


def insert_customers(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into customers (full_name, email, balance)
        values %s;
        """,
        CUSTOMERS,
    )


def insert_products(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into products (product_name, price, stock_quantity)
        values %s;
        """,
        PRODUCTS,
    )


def insert_orders(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into orders (customer_id, total_amount)
        values %s;
        """,
        ORDERS,
    )


def insert_order_items(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into order_items (order_id, product_id, quantity, price)
        values %s;
        """,
        ORDER_ITEMS,
    )


def update_order_totals(cursor) -> None:
    cursor.execute(
        """
        update orders o
        set total_amount = coalesce(t.total_amount, 0)
        from (
            select
                order_id,
                sum(quantity * price) as total_amount
            from order_items
            group by order_id
        ) t
        where o.order_id = t.order_id;
        """
    )


def reduce_stock(cursor) -> None:
    cursor.execute(
        """
        update products p
        set stock_quantity = p.stock_quantity - t.total_quantity
        from (
            select
                product_id,
                sum(quantity) as total_quantity
            from order_items
            group by product_id
        ) t
        where p.product_id = t.product_id;
        """
    )


def print_summary(cursor) -> None:
    cursor.execute("select count(*) from customers;")
    customers_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from products;")
    products_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from orders;")
    orders_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from order_items;")
    order_items_count = cursor.fetchone()[0]

    print("Seed completed successfully.")
    print(f"Customers inserted: {customers_count}")
    print(f"Products inserted: {products_count}")
    print(f"Orders inserted: {orders_count}")
    print(f"Order items inserted: {order_items_count}")


def main() -> None:
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection:
            with connection.cursor() as cursor:
                validate_schema(cursor)
                clear_tables(cursor)
                insert_customers(cursor)
                insert_products(cursor)
                insert_orders(cursor)
                insert_order_items(cursor)
                update_order_totals(cursor)
                reduce_stock(cursor)
                print_summary(cursor)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
