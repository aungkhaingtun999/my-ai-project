/*
  012_refund_sale_rpc.sql
  Function: fn_refund_sale
  Logic: Refund record တင် + Stock ပြန်တိုး
*/

CREATE OR REPLACE FUNCTION fn_refund_sale(
    p_sale_id bigint,
    p_warehouse_id bigint,
    p_items jsonb -- ပြန်အမ်းမည့် ပစ္စည်းစာရင်း [{product_id, qty}]
) RETURNS void AS $$
DECLARE
    item record;
BEGIN
    -- 1. Refund Record အသစ်ထည့်ခြင်း
    INSERT INTO refunds (sale_id, refund_date)
    VALUES (p_sale_id, now());

    -- 2. Items တစ်ခုချင်းစီအတွက် Loop ပတ်ခြင်း
    FOR item IN 
        SELECT * FROM jsonb_to_recordset(p_items) 
        AS x(product_id bigint, qty integer)
    LOOP
        -- Warehouse Stock ပြန်တိုးခြင်း
        UPDATE warehouse_stock
        SET qty = qty + item.qty
        WHERE product_id = item.product_id AND warehouse_id = p_warehouse_id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
