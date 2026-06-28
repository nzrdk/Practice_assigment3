CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    balance NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    stock_quantity INT NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE order_log (
    log_id SERIAL PRIMARY KEY,
    order_id INT,
    customer_id INT,
    action VARCHAR(50),
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INT)
RETURNS NUMERIC AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(quantity * price), 0)
    INTO v_total
    FROM order_items
    WHERE order_id = p_order_id;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE create_order(p_customer_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM customers WHERE customer_id = p_customer_id) THEN
        RAISE EXCEPTION 'Customer with ID % does not exist.', p_customer_id;
    END IF;

    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES (p_customer_id, CURRENT_TIMESTAMP, 0);
END;
$$;

CREATE OR REPLACE PROCEDURE add_product_to_order(
    p_order_id INT,
    p_product_id INT,
    p_quantity INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_price NUMERIC;
    v_stock INT;
BEGIN
    IF p_quantity <= 0 THEN
        RAISE EXCEPTION 'Quantity must be greater than zero.';
    END IF;

    SELECT price, stock_quantity
    INTO v_price, v_stock
    FROM products
    WHERE product_id = p_product_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product with ID % does not exist.', p_product_id;
    END IF;

    IF v_stock < p_quantity THEN
        RAISE EXCEPTION 'Not enough stock. Available: %, Requested: %', v_stock, p_quantity;
    END IF;

    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES (p_order_id, p_product_id, p_quantity, v_price);

    UPDATE products
    SET stock_quantity = stock_quantity - p_quantity
    WHERE product_id = p_product_id;

END;
$$;

CREATE OR REPLACE FUNCTION trigger_update_order_total_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE orders
        SET total_amount = calculate_order_total(OLD.order_id)
        WHERE order_id = OLD.order_id;
        RETURN OLD;
    ELSE
        UPDATE orders
        SET total_amount = calculate_order_total(NEW.order_id)
        WHERE order_id = NEW.order_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_order_total_trigger
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW
EXECUTE FUNCTION trigger_update_order_total_func();

CREATE OR REPLACE FUNCTION trigger_order_audit_log_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO order_log (order_id, customer_id, action)
    VALUES (NEW.order_id, NEW.customer_id, 'Order Created');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_audit_log_trigger
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION trigger_order_audit_log_func();