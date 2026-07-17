/*
  010_create_product_full_function.sql
  Description: Product အသစ် Create လုပ်ရင် Warehouse Stock မှာပါ အလိုအလျောက် Record တင်ပေးမည့် Function
*/

CREATE OR REPLACE FUNCTION fn_create_product(
    p_name text,
    p_sku text,
    p_price numeric,
    p_warehouse_id bigint
) RETURNS bigint AS $$
DECLARE
    v_product_id bigint;
BEGIN
    -- 1. Product အသစ်ထည့်ခြင်း
    INSERT INTO products (name, sku, price)
    VALUES (p_name, p_sku, p_price)
    RETURNING id INTO v_product_id;

    -- 2. Warehouse Stock မှာ စတင် Record ထည့်ခြင်း (Initial stock = 0)
    INSERT INTO warehouse_stock (product_id, warehouse_id, qty)
    VALUES (v_product_id, p_warehouse_id, 0);

    RETURN v_product_id;
END;
$$ LANGUAGE plpgsql;
