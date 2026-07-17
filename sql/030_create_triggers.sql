-- Stock နုတ်တဲ့အခါ 0 အောက်ရောက်သွားရင် Error တက်စေမည့် Trigger
CREATE OR REPLACE FUNCTION fn_check_stock_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.qty < 0 THEN
        RAISE EXCEPTION 'Stock မလုံလောက်ပါ!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_stock_qty
BEFORE UPDATE ON warehouse_stock
FOR EACH ROW
EXECUTE FUNCTION fn_check_stock_limit();
