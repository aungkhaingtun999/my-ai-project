CREATE OR REPLACE VIEW view_inventory_status AS
SELECT 
    w.name AS warehouse_name,
    p.name AS product_name,
    s.qty,
    p.reorder_level
FROM warehouse_stock s
JOIN warehouses w ON s.warehouse_id = w.id
JOIN products p ON s.product_id = p.id;
