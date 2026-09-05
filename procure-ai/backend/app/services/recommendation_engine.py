from sqlalchemy.orm import Session
import uuid
from typing import List, Dict, Any
from app.models.procurement import SupplierQuote, SupplierQuoteItem, RFQItem
from app.models.suppliers import Supplier
from app.models.advanced import ProcurementRecommendation

def compare_quotes(rfq_id: uuid.UUID, db: Session) -> Dict[str, Any]:
    """Deterministic scoring of supplier quotes for a given RFQ.
    Returns a dict with ranked quotes and a best match.
    """
    # Load RFQ items (assume a single item for simplicity)
    rfq_items: List[RFQItem] = db.query(RFQItem).filter(RFQItem.rfq_id == rfq_id).all()
    if not rfq_items:
        raise ValueError("No RFQ items found for the given rfq_id")
    rfq_item = rfq_items[0]
    required_qty = rfq_item.quantity

    # Load all supplier quotes linked to this RFQ
    quotes: List[SupplierQuote] = db.query(SupplierQuote).filter(SupplierQuote.rfq_id == rfq_id).all()
    if not quotes:
        raise ValueError("No supplier quotes found for the given RFQ")

    # Gather price information for normalization (cheapest price gets highest weight)
    prices = []
    for q in quotes:
        q_item = (
            db.query(SupplierQuoteItem)
            .filter(SupplierQuoteItem.quote_id == q.id, SupplierQuoteItem.rfq_item_id == rfq_item.id)
            .first()
        )
        if q_item and q_item.unit_price is not None:
            prices.append(q_item.unit_price)
    min_price = min(prices) if prices else 0.0

    scored = []
    for q in quotes:
        q_item = (
            db.query(SupplierQuoteItem)
            .filter(SupplierQuoteItem.quote_id == q.id, SupplierQuoteItem.rfq_item_id == rfq_item.id)
            .first()
        )
        if not q_item:
            continue
        supplier = db.query(Supplier).filter(Supplier.id == q.supplier_id).first()
        criteria: Dict[str, Any] = {}
        score = 0.0

        # Quantity vs required quantity (hard filter)
        meets_qty = q_item.quoted_quantity is not None and q_item.quoted_quantity >= required_qty
        criteria["meets_quantity"] = meets_qty
        score += 20 if meets_qty else -10

        # MOQ feasibility (hard filter)
        moq_feasible = q_item.moq is None or q_item.moq <= required_qty
        criteria["moq_feasible"] = moq_feasible
        score += 10 if moq_feasible else -5

        # Delivery lead time (penalty for long lead times)
        lead_time = q_item.lead_time_days if q_item.lead_time_days is not None else 9999
        criteria["lead_time"] = lead_time
        score -= lead_time * 0.5  # weight factor

        # Price (cheaper gets higher score, normalized)
        price_score = (min_price / q_item.unit_price) * 30 if q_item.unit_price else 0
        criteria["price_score"] = price_score
        score += price_score

        # Supplier reliability (multiplicative weight)
        reliability = getattr(supplier, "reliability_score", 1.0) or 1.0
        criteria["reliability"] = reliability
        score *= reliability

        scored.append({
            "quote_id": str(q.id),
            "supplier_id": str(q.supplier_id),
            "score": score,
            "criteria": criteria,
            "unit_price": q_item.unit_price,
            "lead_time_days": lead_time,
            "quoted_quantity": q_item.quoted_quantity,
            "moq": q_item.moq,
        })

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    best = ranked[0] if ranked else None
    return {"rfq_id": str(rfq_id), "ranked_quotes": ranked, "best_match": best}
