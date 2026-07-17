/*
  013_transfer_stock_rpc.sql
  Function: fn_transfer_stock
  Logic: Stock ရွှေ့ပြောင်းခြင်း (Transfer)
*/

CREATE OR REPLACE FUNCTION fn_transfer_stock(
    p_product_id bigint,
    p_from_warehouse_id bigint,
    p_to_warehouse_id bigint,
    p_qty integer
) RETURNS void AS $$
BEGIN
    -- 1. Source Warehouse ကနေ Stock နုတ်ခြင်း
    UPDATE warehouse_stock
    SET qty = qty - p_qty
    WHERE product_id = p_product_id AND warehouse_id = p_from_warehouse_id;

    -- 2. Destination Warehouse မှာ Stock တိုးပေးခြင်း
    INSERT INTO warehouse_stock (product_id, warehouse_id, qty)
    VALUES (p_product_id, p_to_warehouse_id, p_qty)
    ON CONFLICT (product_id, warehouse_id) 
    DO UPDATE SET qty = warehouse_stock.qty + EXCLUDED.qty;
    
    -- 3. Transfer မှတ်တမ်းတင်ခြင်း
    INSERT INTO stock_transfers (product_id, from_warehouse_id, to_warehouse_id, qty, transfer_date)
    VALUES (p_product_id, p_from_warehouse_id, p_to_warehouse_id, p_qty, now());
END;
$$ LANGUAGE plpgsql;
