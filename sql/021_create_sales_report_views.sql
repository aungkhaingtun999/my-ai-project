CREATE OR REPLACE VIEW view_daily_sales_report AS
SELECT 
    date_trunc('day', sale_date) AS sale_day,
    count(id) AS total_transactions,
    sum(total_amount) AS total_revenue
FROM sales
GROUP BY 1;
