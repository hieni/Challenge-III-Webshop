-- Useful Queries for WebShop Database

-- 1. Get all products with their category names
SELECT p.product_id, p.name, p.description, p.price, p.stock, c.category_name
FROM product p
    JOIN category c ON p.category_id = c.category_id
ORDER BY p.name;

-- 2. Get all orders for a specific customer with total amounts
SELECT o.order_id, o.order_date, o.status, o.total_amount, c.first_name, c.last_name, c.email
FROM "order" o
    JOIN customer c ON o.customer_id = c.customer_id
WHERE
    c.customer_id = 1
ORDER BY o.order_date DESC;

-- 3. Get order details with all items
SELECT
    o.order_id,
    o.order_date,
    o.status,
    c.first_name || ' ' || c.last_name AS customer_name,
    p.name AS product_name,
    oi.quantity,
    oi.price_per_unit,
    (
        oi.quantity * oi.price_per_unit
    ) AS item_total
FROM
    "order" o
    JOIN customer c ON o.customer_id = c.customer_id
    JOIN order_item oi ON o.order_id = oi.order_id
    JOIN product p ON oi.product_id = p.product_id
ORDER BY o.order_id, oi.order_item_id;

-- 4. Get cart contents for a specific customer
SELECT
    c.first_name || ' ' || c.last_name AS customer_name,
    p.name AS product_name,
    p.price,
    ci.quantity,
    (p.price * ci.quantity) AS subtotal
FROM
    cart ca
    JOIN customer c ON ca.customer_id = c.customer_id
    JOIN cart_item ci ON ca.cart_id = ci.cart_id
    JOIN product p ON ci.product_id = p.product_id
WHERE
    c.customer_id = 1;

-- 5. Get total cart value for each customer
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(ci.cart_item_id) AS items_in_cart,
    SUM(p.price * ci.quantity) AS cart_total
FROM
    customer c
    JOIN cart ca ON c.customer_id = ca.customer_id
    JOIN cart_item ci ON ca.cart_id = ci.cart_id
    JOIN product p ON ci.product_id = p.product_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name;

-- 6. Get best selling products
SELECT
    p.product_id,
    p.name,
    p.price,
    SUM(oi.quantity) AS total_sold,
    SUM(
        oi.quantity * oi.price_per_unit
    ) AS total_revenue
FROM product p
    JOIN order_item oi ON p.product_id = oi.product_id
GROUP BY
    p.product_id,
    p.name,
    p.price
ORDER BY total_sold DESC
LIMIT 10;

-- 7. Get products that are low in stock (less than 10 items)
SELECT p.product_id, p.name, p.price, p.stock, c.category_name
FROM product p
    JOIN category c ON p.category_id = c.category_id
WHERE
    p.stock < 10
ORDER BY p.stock ASC;

-- 8. Get customer order history with total spent
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customer c
    LEFT JOIN "order" o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email
ORDER BY total_spent DESC;

-- 9. Get products by category with stock information
SELECT
    c.category_name,
    COUNT(p.product_id) AS product_count,
    SUM(p.stock) AS total_stock,
    AVG(p.price) AS average_price
FROM category c
    LEFT JOIN product p ON c.category_id = p.category_id
GROUP BY
    c.category_name
ORDER BY product_count DESC;

-- 10. Get recent orders (last 30 days)
SELECT o.order_id, o.order_date, o.status, c.first_name || ' ' || c.last_name AS customer_name, o.total_amount
FROM "order" o
    JOIN customer c ON o.customer_id = c.customer_id
WHERE
    o.order_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY o.order_date DESC;