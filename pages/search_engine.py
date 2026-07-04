def normalize(v):
    return str(v or "").lower().strip()


def search_products(products, keyword):
    keyword = normalize(keyword)

    if not keyword:
        return []

    scored = []

    for p in products:

        name = normalize(p.get("name"))
        barcode = normalize(p.get("barcode"))
        sku = normalize(p.get("sku"))

        score = 0

        if keyword == name:
            score += 1000
        if keyword == barcode:
            score += 950
        if keyword == sku:
            score += 900

        if name.startswith(keyword):
            score += 600
        if barcode.startswith(keyword):
            score += 550
        if sku.startswith(keyword):
            score += 500

        if keyword in name:
            score += 300
        if keyword in barcode:
            score += 250
        if keyword in sku:
            score += 200

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [p for _, p in scored]