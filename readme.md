This is a database system for managing online store orders, including PL/pgSQL procedures and triggers



# Practice Assignment 3

**Total: 10 points**  
**Bonus Tasks: +3 points**

## Topic

Students must create a small database system for managing orders in an online store.

The goal of this assignment is to practice:

- SQL functions;
- SQL procedures;
- triggers;
- audit logging;
- testing database logic;
- basic Git workflow;
- basic query analysis with `EXPLAIN ANALYZE`.

---

# Database Structure

Use the following tables:

```sql
create table customers (
    customer_id serial primary key,
    full_name varchar(100) not null,
    email varchar(100) unique not null,
    balance numeric(10,2) default 0
);

create table products (
    product_id serial primary key,
    product_name varchar(100) not null,
    price numeric(10,2) not null,
    stock_quantity int not null
);

create table orders (
    order_id serial primary key,
    customer_id int references customers(customer_id),
    order_date timestamp default current_timestamp,
    total_amount numeric(10,2) default 0
);

create table order_items (
    order_item_id serial primary key,
    order_id int references orders(order_id),
    product_id int references products(product_id),
    quantity int not null,
    price numeric(10,2) not null
);

create table order_log (
    log_id serial primary key,
    order_id int,
    customer_id int,
    action varchar(50),
    log_date timestamp default current_timestamp
);
```

---

# Main Tasks — 10 Points

## Task 1 — Function: Calculate Order Total  
**2 points**

Create a function:

```sql
calculate_order_total(p_order_id int)
```

The function must return the total value of an order.

The total should be calculated using data from `order_items`:

```sql
quantity * price
```

Expected result:

- If the order has products, return the sum of all order items.
- If the order has no products, return `0`.

---

## Task 2 — Procedure: Create New Order  
**2 points**

Create a procedure:

```sql
create_order(p_customer_id int)
```

The procedure must create a new order for the selected customer.

Requirements:

- Insert a new row into the `orders` table.
- Set `total_amount` to `0`.
- Use the current timestamp as `order_date`.
- The procedure should not insert an order for a non-existing customer.

---

## Task 3 — Procedure: Add Product to Order  
**2 points**

Create a procedure:

```sql
add_product_to_order(
    p_order_id int,
    p_product_id int,
    p_quantity int
)
```

The procedure must add a product to an order.

Requirements:

- Insert a row into `order_items`.
- Use the current product price from the `products` table.
- Decrease `products.stock_quantity`.
- Prevent adding a product if there is not enough stock.
- Prevent adding zero or negative quantity.

---

## Task 4 — Trigger: Update Order Total  
**2 points**

Create a trigger that automatically recalculates `orders.total_amount` whenever data in `order_items` changes.

The trigger must work after:

- inserting a new order item;
- updating quantity or price;
- deleting an order item.

The trigger should use the function from Task 1.

---

## Task 5 — Trigger: Order Audit Log  
**1 point**

Create a trigger that writes a record into the `order_log` table after a new order is created.

The log record should contain:

- order id;
- customer id;
- action type;
- timestamp.
---

## Task 6 — Testing  
**1 point**

Demonstrate that the created functions, procedures, and triggers work correctly.

Your test script should show that:

- customers can be created;
- products can be created;
- orders can be created using the procedure;
- products can be added to orders using the procedure;
- order totals are updated automatically;
- product stock decreases correctly;
- order creation is logged in `order_log`.

---

# Bonus Tasks — 3 Points

## Bonus Task 1 — Version Control with Git  
**1 point**

Create a Git repository for this assignment.

Requirements:

- Make at least **3 meaningful commits**.
- Commit messages must clearly describe the changes.
- Submit a screenshot of the commit history or provide a link to the repository.

Example commit messages:

```text
Initial database schema
Added order procedures
Implemented triggers and tests
```

---

## Bonus Task 2 — Theory Questions  
**1 point**

Create a file named `answers.md` and answer the following questions:

1. What is the difference between a function and a procedure in PostgreSQL?
2. Can a trigger be executed manually? Why or why not?
3. What are the advantages and disadvantages of storing business logic inside the database?

Each answer should be concise: **2–5 sentences**.

---

## Bonus Task 3 — Query Analysis  
**1 point**

Use:

```sql
EXPLAIN ANALYZE
```

on a query that retrieves all products from one order.

Example query:

```sql
explain analyze
select
    oi.order_id,
    p.product_name,
    oi.quantity,
    oi.price,
    oi.quantity * oi.price as item_total
from order_items oi
join products p on oi.product_id = p.product_id
where oi.order_id = 1;
```

Submit:

- the execution plan;
- a short explanation of how PostgreSQL executes the query;
- identification of whether PostgreSQL uses a Sequential Scan, Index Scan, Hash Join, Nested Loop, or another operation.

The explanation should be **3–5 sentences**.

---

# Submission Requirements

Students must submit:

1. SQL script with all tables, functions, procedures, and triggers.
2. `README.md` with a short description of the solution.
3. `answers.md` for the theory bonus task, if completed.
4. Link to Git commit history, if completed.
5. Screenshot or copied output from `EXPLAIN ANALYZE`, if completed.

Maximum score: **13 points**.
