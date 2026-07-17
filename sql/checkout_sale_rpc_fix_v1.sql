-- ==========================================
-- ERP ENTERPRISE
-- FIX checkout_sale_rpc
-- Compatible with POS v4
-- ==========================================

CREATE OR REPLACE FUNCTION checkout_sale_rpc(
    p_cart jsonb,
    p_paid_amount numeric,
    p_cashier_id uuid DEFAULT NULL::uuid
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    v_sale_id bigint;
    v_invoice_no text;
    item jsonb;

BEGIN

    -- Generate Invoice
    v_invoice_no := 'INV-' || to_char(now(),'YYYYMMDDHH24MISS');


    -- Insert Sale Header
    INSERT INTO sales
    (
        invoice_no,
        total_amount,
        cashier_id,
        created_at
    )
    VALUES
    (
        v_invoice_no,
        p_paid_amount,
        p_cashier_id,
        now()
    )
    RETURNING id INTO v_sale_id;



    -- Insert Sale Items
    FOR item IN
        SELECT * FROM jsonb_array_elements(p_cart)
    LOOP

        INSERT INTO sale_items
        (
            sale_id,
            product_id,
            qty,
            price
        )
        VALUES
        (
            v_sale_id,

            COALESCE(
                (item->>'product_id')::bigint,
                (item->>'id')::bigint
            ),

            (item->>'qty')::integer,

            COALESCE(
                (item->>'cost')::numeric,
                (item->>'selling_price')::numeric
            )
        );

    END LOOP;



    RETURN jsonb_build_object(
        'success', true,
        'invoice_no', v_invoice_no,
        'sale_id', v_sale_id
    );


EXCEPTION WHEN OTHERS THEN

    RETURN jsonb_build_object(
        'success', false,
        'message', SQLERRM
    );

END;
$$;