
-- 1. Receita total por mês nos últimos 6 meses
SELECT strftime('%Y-%m', order_date) AS month, ROUND(SUM(total_amount), 2) AS total_revenue
FROM orders
WHERE order_date >= '2024-07-01' AND order_date <= '2024-12-31' AND status = 'Entregue'
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- 2. Top 5 produtos por receita
SELECT p.product_name, p.category, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Entregue'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;

-- 3. Receita por categoria de produto
SELECT p.category, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Entregue'
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 4. Número de clientes únicos por mês
SELECT strftime('%Y-%m', order_date) AS month, COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- 5. Ticket médio por cliente
SELECT c.customer_id, c.customer_name, ROUND(AVG(o.total_amount), 2) AS avg_ticket
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Entregue'
GROUP BY c.customer_id, c.customer_name
ORDER BY avg_ticket DESC;

-- 6. Top 10 clientes por valor total de compras
SELECT c.customer_id, c.customer_name, ROUND(SUM(o.total_amount), 2) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Entregue'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 10;

-- 7. Produtos mais vendidos (por quantidade)
SELECT p.product_name, p.category, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Entregue'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_quantity DESC
LIMIT 10;

-- 8. Média de preço por categoria
SELECT category, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;
