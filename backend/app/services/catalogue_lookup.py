"""Exact SKU and full product-name lookups, no LLM tokens for verified simple fields.
Avoid fuzzy/ambiguous price claims. All queries must have tenant and KB scope.
"""
import re
from sqlalchemy import select
from app.db.models import Product

PRICE_WORDS = ('price', 'cost', 'how much', 'rate', 'qeemat', 'kitnay', 'kitne')
STOCK_WORDS = ('stock', 'available', 'availability', 'in stock')

def lookup_product_answer(db, *, company_id, kb_id, question):
    q = question.casefold().strip()
    if not any(k in q for k in PRICE_WORDS + STOCK_WORDS):
        return None
    products = db.scalars(select(Product).where(Product.company_id == company_id, Product.kb_id == kb_id)).all()
    found = []
    for p in products:
        sku = p.sku.strip().casefold()
        name = p.name.strip().casefold()
        if ((sku and re.search(r'(?<!\w)' + re.escape(sku) + r'(?!\w)', q)) or
            (name and re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', q))):
            found.append(p)
    if len(found) != 1:
        return None
    p = found[0]
    if any(k in q for k in PRICE_WORDS) and p.price.strip():
        return f'**{p.name}** is listed at **{p.price} {p.currency}** in the company catalogue. Prices can change; please confirm before ordering.'
    if any(k in q for k in STOCK_WORDS) and p.availability.strip():
        return f'The catalogue lists **{p.name}** as **{p.availability}**. Please confirm current stock before ordering.'
    return None
