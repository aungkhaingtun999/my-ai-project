CREATE OR REPLACE FUNCTION create_product_full(
  p_data jsonb, 
  p_warehouse_id bigint, 
  p_initial_qty int
) RETURNS TABLE(response_json json) AS $$
DECLARE
  v_product_id bigint;
  v_sku text := trim(p_data->>'sku');
  v_name text := trim(p_data->>'name');
  v_barcode text := trim(p_data->>'barcode');
BEGIN
  -- 1. Input Validation
  IF v_name = '' THEN RAISE EXCEPTION 'Product name is required'; END IF;
  IF v_sku = '' THEN RAISE EXCEPTION 'SKU is required'; END IF;
  IF p_initial_qty < 0 THEN RAISE EXCEPTION 'Initial quantity cannot be negative'; END IF;

  -- 2. Warehouse Validation
  IF NOT EXISTS (SELECT 1 FROM warehouses WHERE id = p_warehouse_id AND is_active = TRUE) THEN
    RAISE EXCEPTION 'Warehouse not found or inactive';
  END IF;

  -- 3. Duplicate Checks (SKU & Barcode)
  IF EXISTS (SELECT 1 FROM products WHERE sku = v_sku AND is_active = TRUE) THEN
    RAISE EXCEPTION 'SKU % already exists', v_sku;
  END IF;
  
  IF v_barcode <> '' AND EXISTS (SELECT 1 FROM products WHERE barcode = v_barcode AND is_active = TRUE) THEN
    RAISE EXCEPTION 'Barcode % already exists', v_barcode;
  END IF;

  -- 4. Insert Product (with COALESCE for safety)
  INSERT INTO products (
    name, sku, barcode, purchase_price, selling_price, category, unit, minimum_stock, is_active
  ) VALUES (
    v_name, 
    v_sku, 
    v_barcode, 
    COALESCE((p_data->>'purchase_price')::numeric, 0), 
    COALESCE((p_data->>'selling_price')::numeric, 0), 
    p_data->>'category', 
    p_data->>'unit', 
    COALESCE((p_data->>'minimum_stock')::int, 0),
    TRUE
  ) RETURNING id INTO v_product_id;

  -- 5. Insert Warehouse Stock
  INSERT INTO warehouse_stock (product_id, warehouse_id, qty)
  VALUES (v_product_id, p_warehouse_id, p_initial_qty);

  -- 6. Inventory & Audit Logs
  INSERT INTO inventory_logs (product_id, warehouse_id, qty_before, qty_change, qty_after, transaction_type, reason, created_at)
  VALUES (v_product_id, p_warehouse_id, 0, p_initial_qty, p_initial_qty, 'INITIAL', 'Opening Stock', NOW());

  INSERT INTO audit_logs (table_name, action, record_id, changed_by, created_at)
  VALUES ('products', 'INSERT', v_product_id, 'SYSTEM', NOW());

  -- 7. Success Response
  response_json := json_build_object('status', 'success', 'message', 'Product created successfully', 'product_id', v_product_id);
  RETURN NEXT;

EXCEPTION WHEN OTHERS THEN
  response_json := json_build_object('status', 'error', 'message', SQLERRM);
  RETURN NEXT;
END;
$$ LANGUAGE plpgsql;
