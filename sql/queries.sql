-- 1_top10_customers_90d

SELECT c.customer_id, c.city,
       ROUND(SUM(o.total_amount)::numeric, 2) AS total_spend
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.created_at >= NOW() - INTERVAL '90 days'
GROUP BY c.customer_id, c.city
ORDER BY total_spend DESC
LIMIT 10;


-- 2_top10_products_revenue

SELECT p.product_id, p.category,
       ROUND(SUM(oi.quantity * oi.unit_price)::numeric, 2) AS total_revenue,
       ROUND(SUM(CASE WHEN o.created_at >= NOW() - INTERVAL '30 days'
                      THEN oi.quantity * oi.unit_price ELSE 0 END)::numeric, 2) AS revenue_last_30d
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id   = oi.order_id
GROUP BY p.product_id, p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- 3_monthly_revenue_12m

SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
       ROUND(SUM(total_amount)::numeric, 2)                AS revenue
FROM orders
WHERE created_at >= NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY DATE_TRUNC('month', created_at);


-- 4_repeat_purchase_rate

SELECT
    COUNT(DISTINCT customer_id)                                            AS total_customers,
    COUNT(DISTINCT CASE WHEN order_count >= 2 THEN customer_id END)        AS repeat_customers,
    ROUND(COUNT(DISTINCT CASE WHEN order_count >= 2 THEN customer_id END)
          * 100.0 / COUNT(DISTINCT customer_id), 2)                        AS repeat_rate_pct
FROM (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
) t;


-- 5_rfm_segmentation

WITH rfm_raw AS (
    SELECT
        customer_id,
        EXTRACT(DAY FROM NOW() - MAX(created_at))::int   AS recency_days,
        COUNT(*)                                          AS frequency,
        SUM(total_amount)                                 AS monetary
    FROM orders
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT *,
        NTILE(3) OVER (ORDER BY recency_days ASC)  AS r_score,  -- lower days = better
        NTILE(3) OVER (ORDER BY frequency DESC)    AS f_score,
        NTILE(3) OVER (ORDER BY monetary DESC)     AS m_score
    FROM rfm_raw
)
SELECT
    CASE
        WHEN r_score = 3 AND f_score = 3 THEN 'Champions'
        WHEN r_score >= 2 AND f_score >= 2 THEN 'Loyal'
        WHEN r_score = 3                   THEN 'Recent'
        WHEN f_score = 1 AND m_score = 1   THEN 'At Risk'
        ELSE 'Others'
    END AS segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(monetary)::numeric, 2) AS avg_spend
FROM rfm_scored
GROUP BY segment
ORDER BY customer_count DESC;


-- 6_data_quality_mismatched_totals

SELECT o.order_id,
       o.total_amount                                        AS recorded_total,
       ROUND(SUM(oi.quantity * oi.unit_price)::numeric, 2)  AS calculated_total,
       ABS(o.total_amount - SUM(oi.quantity * oi.unit_price)) AS difference
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.total_amount
HAVING ABS(o.total_amount - SUM(oi.quantity * oi.unit_price)) > 0.01
LIMIT 20;


