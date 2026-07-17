/*
  011_checkout_sale_rpc.sql
  Function: fn_checkout_sale
  Logic: Sale record တင် + Items ထည့် + Stock နုတ်
*/

CREATE OR REPLACE FUNCTION fn_checkout_sale(
    p_customer_name text,
    p_warehouse_id bigint,
    p_items jsonb -- ပစ္စည်းစာရင်းကို [{product_id, qty, price}, {...}] ပုံစံနဲ့ ပို့မယ်
) RETURNS void AS $$
DECLARE
    v_sale_id bigint;
    item record;
BEGIN
    -- 1. Sale Record အသစ်ထည့်ခြင်း
    INSERT INTO sales (customer_name, sale_date, warehouse_id)
    VALUES (p_customer_name, now(), p_warehouse_id)
    RETURNING id INTO v_sale_id;

    -- 2. Items တစ်ခုချင်းစီအတွက် Loop ပတ်ပြီး Processing လုပ်ခြင်း
    FOR item IN SELECT * FROM jsonb_to_recordset(p_items) AS x(product_id bigint, qty integer, price numeric)
    LOOP
        -- Sale Items ထည့်ခြင်း
        INSERT INTO sale_items (sale_id, product_id, qty, price)
        VALUES (v_sale_id, item.product_id, item.qty, item.price);

        -- Warehouse Stock နုတ်ခြင်း
        UPDATE warehouse_stock
        SET qty = qty - item.qty
        WHERE product_id = item.product_id AND warehouse_id = p_warehouse_id;
        
        -- Stock နုတ်ပြီး 0 အောက်ရောက်သွားရင် Error တက်စေချင်ရင် ဒီမှာ check လုပ်လို့ရပါတယ်
    END LOOP;
END;
$$ LANGUAGE plpgsql;
