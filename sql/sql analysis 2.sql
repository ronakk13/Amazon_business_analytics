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
    ) AS gross_margin_pct

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE o.order_status != 'Cancelled'

GROUP BY
    p.category,
    p.sub_category

ORDER BY
    gross_profit DESC

LIMIT 10;



DESCRIBE returns;


SELECT
    COUNT(DISTINCT oi.order_item_id) AS total_items_sold,

    COUNT(DISTINCT r.order_item_id) AS returned_items,

    ROUND(
        COUNT(DISTINCT r.order_item_id)
        / COUNT(DISTINCT oi.order_item_id) * 100,
        2
    ) AS return_rate_pct

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN returns r
    ON oi.order_item_id = r.order_item_id

WHERE o.order_status != 'Cancelled';



SELECT
    YEAR(o.order_date) AS year,
    MONTH(o.order_date) AS month,

    COUNT(DISTINCT oi.order_item_id) AS total_items_sold,

    COUNT(DISTINCT r.order_item_id) AS returned_items,

    ROUND(
        COUNT(DISTINCT r.order_item_id)
        / COUNT(DISTINCT oi.order_item_id) * 100,
        2
    ) AS return_rate_pct

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN returns r
    ON oi.order_item_id = r.order_item_id

WHERE o.order_status != 'Cancelled' AND year(o.order_date) = 2025

GROUP BY
    YEAR(o.order_date),
    MONTH(o.order_date)

ORDER BY
    year,
    month;
    
    
    
describe sellers;
describe products;


SELECT
    s.seller_id,

    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT oi.order_item_id) AS total_units_sold,

    ROUND(SUM(oi.final_price), 2) AS revenue,

    ROUND(
        SUM(oi.final_price) / COUNT(DISTINCT o.order_id),
        2
    ) AS aov,

    COUNT(DISTINCT r.order_item_id) AS returned_items,

    ROUND(
        COUNT(DISTINCT r.order_item_id)
        / COUNT(DISTINCT oi.order_item_id) * 100,
        2
    ) AS return_rate_pct

FROM sellers s

JOIN products p
    ON s.seller_id = p.seller_id

JOIN order_items oi
    ON p.product_id = oi.product_id

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN returns r
    ON oi.order_item_id = r.order_item_id

WHERE o.order_status != 'Cancelled'

GROUP BY s.seller_id

ORDER BY return_rate_pct desc
limit 20; 



SELECT
    s.state,

    COUNT(DISTINCT oi.order_item_id) AS total_items_sold,
    COUNT(DISTINCT r.order_item_id) AS returned_items,

    ROUND(
        COUNT(DISTINCT r.order_item_id)
        / COUNT(DISTINCT oi.order_item_id) * 100,
        2
    ) AS return_rate_pct,

    ROUND(SUM(oi.final_price), 2) AS revenue

FROM sellers s
JOIN products p
    ON s.seller_id = p.seller_id
JOIN order_items oi
    ON p.product_id = oi.product_id
JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN returns r
    ON oi.order_item_id = r.order_item_id

WHERE o.order_status != 'Cancelled'

GROUP BY s.state

ORDER BY return_rate_pct DESC;


SELECT
    s.city,

    COUNT(DISTINCT oi.order_item_id) AS total_items_sold,
    COUNT(DISTINCT r.order_item_id) AS returned_items,

    ROUND(
        COUNT(DISTINCT r.order_item_id)
        / COUNT(DISTINCT oi.order_item_id) * 100,
        2
    ) AS return_rate_pct,

    ROUND(SUM(oi.final_price), 2) AS revenue

FROM sellers s
JOIN products p
    ON s.seller_id = p.seller_id
JOIN order_items oi
    ON p.product_id = oi.product_id
JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN returns r
    ON oi.order_item_id = r.order_item_id

WHERE o.order_status != 'Cancelled'

GROUP BY s.city

ORDER BY return_rate_pct DESC;



DESCRIBE app_events;


SELECT
    event_name,
    COUNT(*) AS total_events,
    COUNT(DISTINCT customer_id) AS unique_users,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2
    ) AS event_share_pct
FROM app_events
GROUP BY event_name
ORDER BY total_events DESC;


SELECT
    event_name,
    event_status,
    COUNT(*) AS event_count,
    COUNT(DISTINCT customer_id) AS unique_users
FROM app_events
GROUP BY event_name, event_status
ORDER BY event_name, event_count DESC;

SELECT
    event_name,
    COUNT(*) AS total_events,
    ROUND(AVG(page_load_time_ms), 2) AS avg_load_time_ms,
    ROUND(
        AVG(CASE
            WHEN page_load_time_ms > 3000 THEN 1
            ELSE 0
        END) * 100, 2
    ) AS slow_event_pct
FROM app_events
GROUP BY event_name
ORDER BY avg_load_time_ms DESC;


SELECT
    YEAR(event_timestamp) AS year,
    MONTH(event_timestamp) AS month,
    COUNT(*) AS total_events,
    COUNT(DISTINCT customer_id) AS active_users
FROM app_events
WHERE year(event_timestamp) = 2025
GROUP BY
    YEAR(event_timestamp),
    MONTH(event_timestamp)
ORDER BY year, month;



SELECT
    COUNT(DISTINCT CASE WHEN event_name = 'view_product' THEN customer_id END) AS product_view_users,

    COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN customer_id END) AS cart_users,

    COUNT(DISTINCT CASE WHEN event_name = 'view_cart' THEN customer_id END) AS view_cart_users,

    COUNT(DISTINCT CASE WHEN event_name = 'checkout' THEN customer_id END) AS checkout_users,

    COUNT(DISTINCT CASE WHEN event_name = 'purchase' THEN customer_id END) AS purchase_users,

    ROUND(
        COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN customer_id END)
        * 100.0 /
        COUNT(DISTINCT CASE WHEN event_name = 'view_product' THEN customer_id END), 2
    ) AS view_to_cart_pct,

    ROUND(
        COUNT(DISTINCT CASE WHEN event_name = 'view_cart' THEN customer_id END)
        * 100.0 /
        COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN customer_id END), 2
    ) AS cart_to_viewcart_pct,

    ROUND(
        COUNT(DISTINCT CASE WHEN event_name = 'checkout' THEN customer_id END)
        * 100.0 /
        COUNT(DISTINCT CASE WHEN event_name = 'view_cart' THEN customer_id END), 2
    ) AS viewcart_to_checkout_pct,

    ROUND(
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' THEN customer_id END)
        * 100.0 /
        COUNT(DISTINCT CASE WHEN event_name = 'checkout' THEN customer_id END), 2
    ) AS checkout_to_purchase_pct

FROM app_events;




SELECT
    d.brand,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
GROUP BY d.brand
ORDER BY failure_rate_pct DESC;



SELECT
    d.app_version,
    d.brand,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
GROUP BY
    d.app_version,
    d.brand
ORDER BY
    failure_rate_pct DESC;
    
    
SELECT
    d.model,
    COUNT(*) AS total_atc_events,
    d.os_version,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
JOIN customers c 
	ON d.customer_id = c.customer_id
JOIN orders o
	ON c.customer_id = o.customer_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND YEAR(o.order_date) = 2025
  AND MONTH(o.order_date) = 'March'
GROUP BY d.model , d.os_version
ORDER BY failure_rate_pct DESC;



SELECT
    YEAR(ae.event_timestamp) AS year,
    MONTH(ae.event_timestamp) AS month,
    COUNT(*) AS total_atc_events,

    SUM(
        CASE WHEN ae.event_status = 'Success'
        THEN 1 ELSE 0 END
    ) AS successful_atc,

    SUM(
        CASE WHEN ae.event_status = 'Failed'
        THEN 1 ELSE 0 END
    ) AS failed_atc,

    ROUND(
        SUM(
            CASE WHEN ae.event_status = 'Failed'
            THEN 1 ELSE 0 END
        ) * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct

FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id

WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND YEAR(ae.event_timestamp) = 2025
  

GROUP BY
    YEAR(ae.event_timestamp),
    MONTH(ae.event_timestamp)

ORDER BY
    year,
    month;
    
    
    
SELECT
    d.model,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY d.model
ORDER BY failure_rate_pct DESC;



SELECT
    d.model,
    d.os_version,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
  AND d.model IN ('S23', 'A35', 'M34')
GROUP BY d.model, d.os_version
ORDER BY failure_rate_pct DESC;


SELECT
    d.os_version,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY d.os_version
ORDER BY failure_rate_pct DESC;


SELECT
    DAY(ae.event_timestamp) AS day,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY DAY(ae.event_timestamp)
ORDER BY day;



SELECT
    ae.event_name,
    COUNT(*) AS total_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_events,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_events,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY ae.event_name
ORDER BY failure_rate_pct DESC;



SELECT
    ae.event_status,
    COUNT(*) AS total_events,
    ROUND(AVG(ae.page_load_time_ms), 2) AS avg_load_time_ms,
    MIN(ae.page_load_time_ms) AS min_load_time_ms,
    MAX(ae.page_load_time_ms) AS max_load_time_ms
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY ae.event_status;


SELECT
	p.category,
    p.sub_category,
    COUNT(*) AS total_atc_events,
    SUM(CASE WHEN ae.event_status = 'Success' THEN 1 ELSE 0 END) AS successful_atc,
    SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END) AS failed_atc,
    ROUND(
        SUM(CASE WHEN ae.event_status = 'Failed' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
JOIN products p
    ON ae.product_id = p.product_id
WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3
GROUP BY p.sub_category , p.category
ORDER BY failure_rate_pct DESC;

DESCRIBE app_events;


SELECT
    YEAR(ae.event_timestamp) AS year,
    MONTH(ae.event_timestamp) AS month,

    COUNT(*) AS total_atc_events,

    SUM(CASE
        WHEN ae.event_status = 'Success' THEN 1
        ELSE 0
    END) AS successful_atc,

    SUM(CASE
        WHEN ae.event_status = 'Failed' THEN 1
        ELSE 0
    END) AS failed_atc,

    ROUND(
        SUM(CASE
            WHEN ae.event_status = 'Failed' THEN 1
            ELSE 0
        END) * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct

FROM app_events ae

JOIN devices d
    ON ae.device_id = d.device_id

WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'

GROUP BY
    YEAR(ae.event_timestamp),
    MONTH(ae.event_timestamp)

ORDER BY
    year,
    month;
    
    

SELECT
    prev.event_name AS previous_event,
    ae.event_status,
    COUNT(*) AS atc_events
FROM app_events ae

JOIN devices d
    ON ae.device_id = d.device_id

JOIN app_events prev
    ON ae.session_id = prev.session_id
    AND prev.event_timestamp < ae.event_timestamp

WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3

  AND prev.event_timestamp = (
      SELECT MAX(p2.event_timestamp)
      FROM app_events p2
      WHERE p2.session_id = ae.session_id
        AND p2.event_timestamp < ae.event_timestamp
  )

GROUP BY
    prev.event_name,
    ae.event_status

ORDER BY
    previous_event,
    ae.event_status;
    
    
    
    
SELECT
    ae.event_status,
    COUNT(*) AS atc_events,
    ROUND(
        AVG(
            TIMESTAMPDIFF(
                SECOND,
                prev.event_timestamp,
                ae.event_timestamp
            )
        ),
        2
    ) AS avg_seconds_to_atc

FROM app_events ae

JOIN devices d
    ON ae.device_id = d.device_id

JOIN app_events prev
    ON ae.session_id = prev.session_id
    AND prev.event_name = 'view_product'
    AND prev.event_timestamp < ae.event_timestamp

WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3

  AND prev.event_timestamp = (
      SELECT MAX(p2.event_timestamp)
      FROM app_events p2
      WHERE p2.session_id = ae.session_id
        AND p2.event_name = 'view_product'
        AND p2.event_timestamp < ae.event_timestamp
  )

GROUP BY ae.event_status;




SELECT
    c.state,
    COUNT(*) AS total_atc_events,

    SUM(CASE
        WHEN ae.event_status = 'Success' THEN 1
        ELSE 0
    END) AS successful_atc,

    SUM(CASE
        WHEN ae.event_status = 'Failed' THEN 1
        ELSE 0
    END) AS failed_atc,

    ROUND(
        SUM(CASE
            WHEN ae.event_status = 'Failed' THEN 1
            ELSE 0
        END) * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct

FROM app_events ae
JOIN devices d
    ON ae.device_id = d.device_id
JOIN customers c
	ON c.customer_id = d.customer_id

WHERE ae.event_name = 'add_to_cart'
  AND d.brand = 'Samsung'
  AND d.app_version = '5.1'
  AND d.os_version = 'Android 14'
  AND YEAR(ae.event_timestamp) = 2025
  AND MONTH(ae.event_timestamp) = 3

GROUP BY c.state

HAVING COUNT(*) >= 5

ORDER BY failure_rate_pct DESC;