-- ==========================================
-- ERP PURCHASE RECEIVE RPC
-- purchase_receive_rpc
-- ==========================================

CREATE OR REPLACE FUNCTION public.purchase_receive_rpc(
    p_product_id BIGINT,
    p_supplier_id BIGINT,
    p_warehouse_id BIGINT,
    p_qty INTEGER,
    p_price NUMERIC,
    p_notes TEXT DEFAULT '',
    p_created_by UUID DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS
$$
DECLARE
    v_purchase_id BIGINT;
    v_purchase_no TEXT;
    v_stock RECORD;
    v_new_qty INTEGER;
BEGIN

    -- Validation
    IF p_qty <= 0 THEN
        RAISE EXCEPTION 'Quantity must be greater than zero';
    END IF;

    IF p_price < 0 THEN
        RAISE EXCEPTION 'Invalid purchase price';
    END IF;

    -- Purchase Number
    v_purchase_no :=
        'PO-' ||
        TO_CHAR(NOW(),'YYYYMMDDHH24MISS');

    -- Insert Purchase
    INSERT INTO purchases(
        purchase_no,
        supplier_id,
        warehouse_id,
        product_id,
        qty,
        price,
        total,
        net_total,
        notes,
        created_by,
        created_at,
        updated_at
    )
    VALUES(
        v_purchase_no,
        p_supplier_id,
        p_warehouse_id,
        p_product_id,
        p_qty,
        p_price,
        p_qty * p_price,
        p_qty * p_price,
        p_notes,
        p_created_by,
        NOW(),
        NOW()
    )
    RETURNING id
    INTO v_purchase_id;

    -- Warehouse Stock
    SELECT *
    INTO v_stock
    FROM warehouse_stock
    WHERE warehouse_id=p_warehouse_id
      AND product_id=p_product_id;

    IF FOUND THEN

        UPDATE warehouse_stock
        SET
            qty = qty + p_qty,
            available_qty = available_qty + p_qty,
            updated_at = NOW()
        WHERE id=v_stock.id;

        v_new_qty := v_stock.qty + p_qty;

    ELSE

        INSERT INTO warehouse_stock(
            warehouse_id,
            product_id,
            qty,
            available_qty,
            reserved_qty,
            minimum_stock,
            maximum_stock,
            reorder_level,
            updated_at
        )
        VALUES(
            p_warehouse_id,
            p_product_id,
            p_qty,
            p_qty,
            0,
            0,
            0,
            0,
            NOW()
        );

        v_new_qty := p_qty;

    END IF;

    -- Inventory Log
    INSERT INTO inventory_logs(
        product_id,
        warehouse_id,
        reference_type,
        reference_id,
        quantity,
        balance_after,
        remarks,
        created_by,
        created_at
    )
    VALUES(
        p_product_id,
        p_warehouse_id,
        'PURCHASE',
        v_purchase_id,
        p_qty,
        v_new_qty,
        p_notes,
        p_created_by,
        NOW()
    );

    RETURN jsonb_build_object(
        'success', true,
        'purchase_id', v_purchase_id,
        'purchase_no', v_purchase_no
    );

EXCEPTION
WHEN OTHERS THEN

    RETURN jsonb_build_object(
        'success', false,
        'message', SQLERRM
    );

END;
$$;