use amazon_business_analytics;

-- revenue , orders , aov
select 
	month(o.order_date) as months ,
    year(o.order_date) as years , 
    count(o.order_id) as total_orders , 
    sum(o.total_amount)/count(o.order_id) as aov , 
    sum(o.total_amount) as revenue 
from orders o 
left join payments p 
	on o.order_id = p.order_id
where p.payment_status = "Success"
group by months , years
order by years , months;

 -- category
 
 select 	
	pd.category,
    count(distinct oi.order_id) as orders
from products pd left join order_items oi on pd.product_id = oi.product_id
group by pd.category;
select count(*) from orders;
    
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS successful_orders,
    ROUND(SUM(oi.final_price), 2) AS revenue,
    ROUND(
        SUM(oi.final_price) / COUNT(DISTINCT o.order_id),
        2
    ) AS aov
FROM orders o
JOIN payments pay
    ON o.order_id = pay.order_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025
GROUP BY p.category
ORDER BY revenue DESC;

SELECT
    p.category,
    YEAR(o.order_date) AS year,
    COUNT(DISTINCT o.order_id) AS successful_orders,
    ROUND(SUM(oi.final_price), 2) AS revenue
FROM orders o
JOIN payments pay
    ON o.order_id = pay.order_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) IN (2024, 2025)
GROUP BY
    p.category,
    YEAR(o.order_date)
ORDER BY
    p.category,
    year;
    
SELECT
    YEAR(order_date) AS year,
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order,
    COUNT(*) AS total_orders
FROM orders
GROUP BY YEAR(order_date)
ORDER BY year;
 
SELECT
    MONTH(o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS successful_orders,
    ROUND(SUM(o.total_amount), 2) AS revenue,
    ROUND(
        SUM(o.total_amount) / COUNT(DISTINCT o.order_id),
        2
    ) AS aov
FROM orders o
JOIN payments pay
    ON o.order_id = pay.order_id
WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025
GROUP BY MONTH(o.order_date)
ORDER BY month;

SELECT 
    MONTH(o.order_date) AS month,
    p.category AS category,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(
        SUM(oi.final_price) / COUNT(DISTINCT o.order_id),
        2
    ) AS revenue_per_order,
    ROUND(SUM(oi.final_price), 2) AS revenue
FROM orders o 
JOIN payments pay 
    ON o.order_id = pay.order_id
JOIN order_items oi 
    ON o.order_id = oi.order_id
JOIN products p 
    ON p.product_id = oi.product_id
WHERE pay.payment_status = 'Success' 
  AND YEAR(o.order_date) = 2025
GROUP BY 
    MONTH(o.order_date), 
    p.category
ORDER BY
    month,
    revenue DESC;
    
    
SELECT
    MONTH(o.order_date) AS month,
    p.category,

    ROUND(SUM(oi.final_price), 2) AS category_revenue,

    ROUND(
        SUM(oi.final_price) /
        SUM(SUM(oi.final_price)) OVER (
            PARTITION BY MONTH(o.order_date)
        ) * 100,
        2
    ) AS revenue_contribution_pct

FROM orders o

JOIN payments pay
    ON o.order_id = pay.order_id

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    p.category

ORDER BY
    month,
    category_revenue DESC;
    
    
SELECT
    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(p.cost_price * oi.quantity),
        2
    ) AS total_cost,

    ROUND(
        SUM(oi.final_price)
        - SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (
            SUM(oi.final_price)
            - SUM(p.cost_price * oi.quantity)
        )
        / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct

FROM orders o
JOIN payments pay
    ON o.order_id = pay.order_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025;
    
    
SELECT
    p.category,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(p.cost_price * oi.quantity),
        2
    ) AS total_cost,

    ROUND(
        SUM(oi.final_price)
        - SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (
            SUM(oi.final_price)
            - SUM(p.cost_price * oi.quantity)
        ) / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct

FROM orders o

JOIN payments pay
    ON o.order_id = pay.order_id

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY p.category

ORDER BY gross_profit DESC;

SELECT
    p.category,
    p.sub_category,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(p.cost_price * oi.quantity),
        2
    ) AS total_cost,

    ROUND(
        SUM(oi.final_price)
        - SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (
            SUM(oi.final_price)
            - SUM(p.cost_price * oi.quantity)
        ) / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct,

    COUNT(DISTINCT o.order_id) AS successful_orders

FROM orders o

JOIN payments pay
    ON o.order_id = pay.order_id

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    p.category,
    p.sub_category

ORDER BY
    revenue DESC;
    
    
SELECT
    MONTH(o.order_date) AS month,
    p.category,
    p.sub_category,

    SUM(oi.quantity) AS units_sold,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(oi.final_price) / SUM(oi.quantity),
        2
    ) AS avg_selling_price

FROM orders o

JOIN payments pay
    ON o.order_id = pay.order_id

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    p.category,
    p.sub_category

ORDER BY
    month,
    revenue DESC;
    
SELECT
    MONTH(o.order_date) AS month,

    COUNT(DISTINCT o.customer_id) AS active_customers,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(
        COUNT(DISTINCT o.order_id)
        / COUNT(DISTINCT o.customer_id),
        2
    ) AS orders_per_customer

FROM orders o

WHERE YEAR(o.order_date) = 2025
  AND o.order_status != 'Cancelled'

GROUP BY MONTH(o.order_date)
ORDER BY month;

SELECT
    customer_id,
    MIN(order_date) AS first_order_date
FROM orders
WHERE order_status != 'Cancelled'
GROUP BY customer_id
order by customer_id;

WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
)

SELECT
    MONTH(o.order_date) AS month,

    COUNT(DISTINCT CASE
        WHEN MONTH(fo.first_order_date) = MONTH(o.order_date)
         AND YEAR(fo.first_order_date) = YEAR(o.order_date)
        THEN o.customer_id
    END) AS new_customers,

    COUNT(DISTINCT CASE
        WHEN fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')
        THEN o.customer_id
    END) AS repeat_customers,

    COUNT(DISTINCT o.customer_id) AS active_customers

FROM orders o

JOIN first_orders fo
    ON o.customer_id = fo.customer_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025

GROUP BY MONTH(o.order_date)

ORDER BY month;



WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
)

SELECT
    MONTH(o.order_date) AS month,

    COUNT(DISTINCT o.customer_id) AS repeat_customers,

    COUNT(DISTINCT o.order_id) AS repeat_orders,

    ROUND(
        COUNT(DISTINCT o.order_id)
        / COUNT(DISTINCT o.customer_id),
        2
    ) AS orders_per_repeat_customer

FROM orders o

JOIN first_orders fo
    ON o.customer_id = fo.customer_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025
  AND fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')

GROUP BY
    MONTH(o.order_date)

ORDER BY
    month;
    
    

SELECT
    CASE
        WHEN c.prime_member = 1 THEN 'Prime'
        ELSE 'Non-Prime'
    END AS customer_type,

    COUNT(DISTINCT o.customer_id) AS active_customers,

    COUNT(DISTINCT o.order_id) AS successful_orders,

    ROUND(SUM(o.total_amount), 2) AS revenue,

    ROUND(
        COUNT(DISTINCT o.order_id)
        / COUNT(DISTINCT o.customer_id),
        2
    ) AS orders_per_customer,

    ROUND(
        SUM(o.total_amount)
        / COUNT(DISTINCT o.order_id),
        2
    ) AS aov

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN payments pay
    ON o.order_id = pay.order_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    c.prime_member

ORDER BY
    revenue DESC;  
    
    
    
SELECT
    MONTH(o.order_date) AS month,

    CASE
        WHEN c.prime_member = 1 THEN 'Prime'
        ELSE 'Non-Prime'
    END AS customer_type,

    COUNT(DISTINCT o.customer_id) AS active_customers,

    COUNT(DISTINCT o.order_id) AS successful_orders,

    ROUND(SUM(o.total_amount), 2) AS revenue,

    ROUND(
        COUNT(DISTINCT o.order_id)
        / COUNT(DISTINCT o.customer_id),
        2
    ) AS orders_per_customer,

    ROUND(
        SUM(o.total_amount)
        / COUNT(DISTINCT o.order_id),
        2
    ) AS aov

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN payments pay
    ON o.order_id = pay.order_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    c.prime_member

ORDER BY
    month,
    c.prime_member DESC;
    
    
    
    
WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
)

SELECT
    MONTH(o.order_date) AS month,

    CASE
        WHEN c.prime_member = 1 THEN 'Prime'
        ELSE 'Non-Prime'
    END AS customer_type,

    COUNT(DISTINCT o.customer_id) AS active_customers,

    COUNT(DISTINCT CASE
        WHEN fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')
        THEN o.customer_id
    END) AS repeat_customers,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')
            THEN o.customer_id
        END)
        / COUNT(DISTINCT o.customer_id) * 100,
        2
    ) AS repeat_customer_pct

FROM orders o

JOIN customers c
    ON o.customer_id = c.customer_id

JOIN first_orders fo
    ON o.customer_id = fo.customer_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    c.prime_member

ORDER BY
    month,
    c.prime_member DESC;
    
    
    
    
WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
)

SELECT
    MONTH(o.order_date) AS month,

    CASE
        WHEN c.prime_member = 1 THEN 'Prime'
        ELSE 'Non-Prime'
    END AS customer_type,

    COUNT(DISTINCT o.customer_id) AS active_customers,

    COUNT(DISTINCT CASE
        WHEN fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')
        THEN o.customer_id
    END) AS repeat_customers,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN fo.first_order_date < DATE_FORMAT(o.order_date, '%Y-%m-01')
            THEN o.customer_id
        END)
        / COUNT(DISTINCT o.customer_id) * 100,
        2
    ) AS repeat_customer_pct

FROM orders o

JOIN customers c
    ON o.customer_id = c.customer_id

JOIN first_orders fo
    ON o.customer_id = fo.customer_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    c.prime_member

ORDER BY
    month,
    c.prime_member DESC;
    
    

SELECT
    CASE
        WHEN c.prime_member = 1 THEN 'Prime'
        ELSE 'Non-Prime'
    END AS customer_type,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(p.cost_price * oi.quantity),
        2
    ) AS total_cost,

    ROUND(
        SUM(oi.final_price)
        - SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (
            SUM(oi.final_price)
            - SUM(p.cost_price * oi.quantity)
        ) / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN payments pay
    ON o.order_id = pay.order_id

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE pay.payment_status = 'Success'
  AND YEAR(o.order_date) = 2025

GROUP BY
    c.prime_member

ORDER BY
    gross_profit DESC;
    
    


SELECT
    p.category,
    p.sub_category,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(SUM(p.cost_price * oi.quantity), 2) AS total_cost,

    ROUND(
        SUM(oi.final_price) - SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (SUM(oi.final_price) - SUM(p.cost_price * oi.quantity))
        / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct

FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025

GROUP BY p.category , p.sub_category
ORDER BY gross_profit DESC;



SELECT
    MONTH(o.order_date) AS month,
    p.category,
    p.sub_category,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(p.cost_price * oi.quantity),
        2
    ) AS total_cost,

    ROUND(
        SUM(oi.final_price) -
        SUM(p.cost_price * oi.quantity),
        2
    ) AS gross_profit,

    ROUND(
        (
            SUM(oi.final_price) -
            SUM(p.cost_price * oi.quantity)
        ) / SUM(oi.final_price) * 100,
        2
    ) AS gross_margin_pct

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE o.order_status != 'Cancelled'
  AND YEAR(o.order_date) = 2025

GROUP BY
    MONTH(o.order_date),
    p.category,
    p.sub_category

ORDER BY
    month,
    p.category,
    p.sub_category;