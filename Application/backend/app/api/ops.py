from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload, selectinload

from ..deps import Db, require_roles
from ..errors import NotFound
from ..models import (
    AuditLog,
    LedgerAccount,
    LedgerEntry,
    LedgerTransaction,
    Order,
    Payment,
    Payout,
    Product,
    Refund,
    Return,
    Role,
    Shipment,
    Supplier,
    SupplierDocument,
    SupplierOrder,
    Ticket,
    User,
)
from ..services import audit, ledger, reports
from ..services import payouts as payout_service
from ..services import returns as return_service
from ..services import tracking as tracking_service
from ..services.platform_config import CONFIG_LABELS, DEFAULTS, load_config, set_value
from .schemas import (
    ConfigUpdateIn,
    PayoutDecisionIn,
    PayoutRequestIn,
    ReturnDecisionIn,
    ShipmentTrackingIn,
    SupplierCommissionIn,
    TicketUpdateIn,
)
from .serializers import (
    iso,
    order_out,
    payout_out,
    refund_out,
    return_out,
    shipment_out,
    supplier_out,
    ticket_out,
    user_out,
)

router = APIRouter(prefix="/ops", tags=["operations"])

AdminUser = Depends(require_roles(Role.OPS_ADMIN, Role.SUPERADMIN))
FinanceUser = Depends(require_roles(Role.OPS_FINANCE, Role.SUPERADMIN))
StaffUser = Depends(require_roles(Role.OPS_ADMIN, Role.OPS_FINANCE, Role.OPS_SUPPORT, Role.SUPERADMIN))


def _order_query():
    return select(Order).options(
        selectinload(Order.items),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.items),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.supplier),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.shipments).selectinload(
            Shipment.events
        ),
        joinedload(Order.customer),
    )


@router.get("/dashboard")
def dashboard(db: Db, _: User = StaffUser):
    recent = db.scalars(_order_query().order_by(Order.placed_at.desc()).limit(8)).all()
    awaiting = db.scalars(
        select(SupplierOrder)
        .where(SupplierOrder.status == "awaiting_acceptance")
        .options(
            selectinload(SupplierOrder.items),
            selectinload(SupplierOrder.order),
            selectinload(SupplierOrder.supplier),
        )
        .order_by(SupplierOrder.created_at)
        .limit(10)
    ).all()
    return {
        "summary": reports.summary(db),
        "recent_orders": [order_out(order) for order in recent],
        "awaiting_acceptance": [
            {
                "id": so.id,
                "code": so.code,
                "order_code": so.order.code if so.order else None,
                "supplier": so.supplier.trading_name if so.supplier else None,
                "value": so.merchandise_total,
                "items": len(so.items),
                "created_at": iso(so.created_at),
            }
            for so in awaiting
        ],
    }


@router.get("/orders")
def list_orders(
    db: Db,
    _: User = StaffUser,
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
):
    query = _order_query()
    if status_filter:
        query = query.where(Order.status == status_filter)
    if q:
        needle = f"%{q.strip()}%"
        query = query.where(or_(Order.code.ilike(needle), Order.ship_recipient.ilike(needle)))
    orders = db.scalars(query.order_by(Order.placed_at.desc()).limit(limit)).all()
    return {"items": [order_out(order) for order in orders]}


@router.get("/orders/{order_id}")
def get_order(order_id: str, db: Db, _: User = StaffUser):
    order = db.scalar(_order_query().where(Order.id == order_id))
    if order is None:
        raise NotFound("Order not found")
    payments = db.scalars(
        select(Payment).where(Payment.order_id == order.id).order_by(Payment.initiated_at)
    ).all()
    refunds = db.scalars(select(Refund).where(Refund.order_id == order.id)).all()
    returns = db.scalars(select(Return).where(Return.order_id == order.id)).all()
    from .serializers import payment_out

    entity_ids = [order.id, *[p.id for p in payments], *[r.id for r in refunds]]
    events = db.scalars(
        select(AuditLog)
        .where(AuditLog.entity_id.in_(entity_ids))
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    ).all()
    return {
        **order_out(order, detail=True),
        "customer": user_out(order.customer) if order.customer else None,
        "payments": [payment_out(p) for p in payments],
        "refunds": [refund_out(r) for r in refunds],
        "returns": [return_out(r) for r in returns],
        "audit": [
            {
                "action": e.action,
                "actor_role": e.actor_role,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "created_at": iso(e.created_at),
            }
            for e in events
        ],
    }


@router.post("/shipments/{shipment_id}/tracking")
def update_shipment_tracking(
    shipment_id: str,
    payload: ShipmentTrackingIn,
    db: Db,
    actor: User = StaffUser,
):
    shipment = tracking_service.get_shipment(db, shipment_id)
    before = {"status": shipment.status}
    event = tracking_service.override(
        db,
        shipment=shipment,
        status=payload.status,
        note=payload.note,
        actor=actor,
    )
    audit.record(
        db,
        actor=actor,
        action="shipment.tracking_updated",
        entity_type="shipment",
        entity_id=shipment.id,
        before=before,
        after={"status": event.status, "note": event.note},
    )
    db.commit()
    return shipment_out(tracking_service.get_shipment(db, shipment.id))


@router.get("/suppliers")
def list_suppliers(db: Db, _: User = StaffUser):
    return {"items": reports.supplier_directory(db)}


@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: str, db: Db, _: User = StaffUser):
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise NotFound("Supplier not found")
    documents = db.scalars(
        select(SupplierDocument).where(SupplierDocument.supplier_id == supplier_id)
    ).all()
    products = db.scalars(
        select(Product)
        .where(Product.supplier_id == supplier_id)
        .options(selectinload(Product.variants))
        .limit(100)
    ).all()
    return {
        **supplier_out(supplier),
        "tin": supplier.tin,
        "brela_number": supplier.brela_number,
        "payout": {
            "method": supplier.payout_method,
            "provider": supplier.payout_provider,
            "account_name": supplier.payout_account_name,
            "account_number": supplier.payout_account_number,
        },
        "documents": [
            {
                "id": doc.id,
                "type": doc.doc_type,
                "status": doc.status,
                "file_ref": doc.file_ref,
                "notes": doc.notes,
            }
            for doc in documents
        ],
        "balance": payout_service.supplier_balance(db, supplier_id),
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "status": product.status,
                "variants": len(product.variants),
                "stock": sum(v.on_hand for v in product.variants),
            }
            for product in products
        ],
    }


@router.patch("/suppliers/{supplier_id}")
def update_supplier(supplier_id: str, payload: SupplierCommissionIn, db: Db, actor: User = AdminUser):
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise NotFound("Supplier not found")
    before = {"commission_bp": supplier.commission_bp, "status": supplier.status}
    if payload.commission_bp is not None:
        supplier.commission_bp = payload.commission_bp
    if payload.status is not None:
        supplier.status = payload.status
        if payload.status == "verified":
            from ..models import utcnow

            supplier.kyc_verified_at = utcnow()
            for doc in db.scalars(
                select(SupplierDocument).where(SupplierDocument.supplier_id == supplier.id)
            ):
                doc.status = "approved"
                doc.reviewed_by = actor.id
                doc.reviewed_at = utcnow()
        if payload.status == "rejected":
            supplier.rejection_reason = payload.note
    audit.record(
        db,
        actor=actor,
        action="supplier.updated",
        entity_type="supplier",
        entity_id=supplier.id,
        before=before,
        after={"commission_bp": supplier.commission_bp, "status": supplier.status},
    )
    db.commit()
    return supplier_out(supplier)


@router.get("/payouts")
def list_payouts(db: Db, _: User = FinanceUser, status_filter: str | None = Query(default=None, alias="status")):
    query = select(Payout).order_by(Payout.created_at.desc())
    if status_filter:
        query = query.where(Payout.status == status_filter)
    payouts = db.scalars(query).all()
    suppliers = {s.id: s.trading_name for s in db.scalars(select(Supplier)).all()}
    result = []
    for payout in payouts:
        data = payout_out(payout, payout_service.payout_orders(db, payout.id))
        data["supplier_name"] = suppliers.get(payout.supplier_id)
        result.append(data)
    return {"items": result}


@router.get("/payouts/eligible")
def eligible_balances(db: Db, _: User = FinanceUser):
    suppliers = db.scalars(select(Supplier)).all()
    items = []
    for supplier in suppliers:
        balance = payout_service.supplier_balance(db, supplier.id)
        if balance["eligible"] > 0:
            items.append({"supplier": supplier_out(supplier), "balance": balance})
    return {"items": items}


@router.post("/payouts", status_code=status.HTTP_201_CREATED)
def create_payout(payload: PayoutRequestIn, db: Db, actor: User = FinanceUser):
    supplier = db.get(Supplier, payload.supplier_id)
    if supplier is None:
        raise NotFound("Supplier not found")
    payout = payout_service.request(db, supplier=supplier, actor=actor, notes=payload.notes)
    audit.record(
        db,
        actor=actor,
        action="payout.requested",
        entity_type="payout",
        entity_id=payout.id,
        after={"supplier": supplier.code, "amount": payout.amount},
    )
    db.commit()
    return payout_out(payout, payout_service.payout_orders(db, payout.id))


@router.get("/payouts/{payout_id}")
def get_payout(payout_id: str, db: Db, _: User = FinanceUser):
    payout = payout_service.get_payout(db, payout_id)
    data = payout_out(payout, payout_service.payout_orders(db, payout.id))
    supplier = db.get(Supplier, payout.supplier_id)
    data["supplier"] = supplier_out(supplier) if supplier else None
    return data


@router.post("/payouts/{payout_id}/approve")
def approve_payout(payout_id: str, payload: PayoutDecisionIn, db: Db, actor: User = FinanceUser):
    payout = payout_service.get_payout(db, payout_id)
    payout_service.approve(db, payout=payout, actor=actor, note=payload.note)
    audit.record(
        db,
        actor=actor,
        action="payout.approved",
        entity_type="payout",
        entity_id=payout.id,
        after={"amount": payout.amount},
    )
    db.commit()
    return payout_out(payout, payout_service.payout_orders(db, payout.id))


@router.post("/payouts/{payout_id}/reject")
def reject_payout(payout_id: str, payload: PayoutDecisionIn, db: Db, actor: User = FinanceUser):
    payout = payout_service.get_payout(db, payout_id)
    payout_service.reject(db, payout=payout, actor=actor, reason=payload.reason or payload.note or "Rejected")
    audit.record(
        db,
        actor=actor,
        action="payout.rejected",
        entity_type="payout",
        entity_id=payout.id,
        after={"reason": payload.reason},
    )
    db.commit()
    return payout_out(payout, payout_service.payout_orders(db, payout.id))


@router.post("/payouts/{payout_id}/execute")
def execute_payout(payout_id: str, db: Db, actor: User = FinanceUser):
    payout = payout_service.get_payout(db, payout_id)
    payout_service.execute(db, payout=payout, actor=actor)
    audit.record(
        db,
        actor=actor,
        action="payout.paid",
        entity_type="payout",
        entity_id=payout.id,
        after={"amount": payout.amount, "provider_ref": payout.provider_ref},
    )
    db.commit()
    return payout_out(payout, payout_service.payout_orders(db, payout.id))


@router.get("/config")
def get_config(db: Db, _: User = StaffUser):
    values = load_config(db)
    return {
        "values": values,
        "labels": CONFIG_LABELS,
        "defaults": DEFAULTS,
    }


@router.put("/config")
def update_config(payload: ConfigUpdateIn, db: Db, actor: User = AdminUser):
    unknown = [key for key in payload.values if key not in DEFAULTS]
    if unknown:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown settings: {', '.join(unknown)}")
    before = load_config(db)
    for key, value in payload.values.items():
        if isinstance(DEFAULTS[key], int) and not isinstance(value, int):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{key} must be a whole number")
        if isinstance(DEFAULTS[key], bool) and not isinstance(value, bool):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{key} must be true or false")
        set_value(db, key, value, actor.id)
    after = load_config(db)
    audit.record(
        db,
        actor=actor,
        action="config.updated",
        entity_type="config",
        before=before,
        after=after,
    )
    db.commit()
    return {"values": after}


@router.get("/returns")
def list_returns(db: Db, _: User = StaffUser, status_filter: str | None = Query(default=None, alias="status")):
    returns = return_service.list_returns(db, status_filter)
    items = []
    for ret in returns:
        from ..models import OrderItem

        item = db.get(OrderItem, ret.item_id)
        data = return_out(ret, item=item)
        order = db.get(Order, ret.order_id)
        data["order_code"] = order.code if order else None
        items.append(data)
    return {"items": items}


@router.post("/returns/{return_id}/decide")
def decide_return(return_id: str, payload: ReturnDecisionIn, db: Db, actor: User = StaffUser):
    ret = db.get(Return, return_id)
    if ret is None:
        raise NotFound("Return not found")
    return_service.decide(db, ret=ret, actor=actor, approve=payload.approve, note=payload.note)
    audit.record(
        db,
        actor=actor,
        action="return.decided",
        entity_type="return",
        entity_id=ret.id,
        after={"approved": payload.approve},
    )
    db.commit()
    return {"id": ret.id, "status": ret.status}


@router.post("/returns/{return_id}/receive")
def receive_return(return_id: str, db: Db, actor: User = StaffUser, note: str | None = None):
    ret = db.get(Return, return_id)
    if ret is None:
        raise NotFound("Return not found")
    return_service.receive(db, ret=ret, actor=actor, note=note)
    audit.record(
        db,
        actor=actor,
        action="return.refunded",
        entity_type="return",
        entity_id=ret.id,
        after={"amount": ret.refund_amount},
    )
    db.commit()
    return {"id": ret.id, "status": ret.status, "refund_amount": ret.refund_amount}


@router.get("/refunds")
def list_refunds(db: Db, _: User = FinanceUser):
    refunds = db.scalars(select(Refund).order_by(Refund.created_at.desc()).limit(100)).all()
    return {"items": [refund_out(r) for r in refunds]}


@router.get("/tickets")
def list_tickets(db: Db, _: User = StaffUser, status_filter: str | None = Query(default=None, alias="status")):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    tickets = db.scalars(query.limit(100)).all()
    customers = {user.id: user for user in db.scalars(select(User)).all()}
    items = []
    for ticket in tickets:
        data = ticket_out(ticket)
        customer = customers.get(ticket.customer_id)
        data["customer_name"] = customer.full_name if customer else None
        data["customer_email"] = customer.email if customer else None
        order = db.get(Order, ticket.order_id) if ticket.order_id else None
        data["order_code"] = order.code if order else None
        items.append(data)
    return {"items": items}


@router.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, payload: TicketUpdateIn, db: Db, actor: User = StaffUser):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFound("Ticket not found")
    before = {"status": ticket.status, "priority": ticket.priority, "assigned_to": ticket.assigned_to}
    if payload.status is not None:
        ticket.status = payload.status
        if payload.status == "closed":
            from ..models import utcnow

            ticket.closed_at = utcnow()
    if payload.priority is not None:
        ticket.priority = payload.priority
    if payload.assigned_to is not None:
        ticket.assigned_to = payload.assigned_to or actor.id
    audit.record(
        db,
        actor=actor,
        action="ticket.updated",
        entity_type="ticket",
        entity_id=ticket.id,
        before=before,
        after={"status": ticket.status, "priority": ticket.priority},
    )
    db.commit()
    return ticket_out(ticket)


@router.get("/ledger")
def ledger_view(db: Db, _: User = FinanceUser):
    accounts = db.scalars(select(LedgerAccount)).all()
    balances = [
        {
            "code": account.code,
            "name": account.name,
            "kind": account.kind,
            "balance": ledger.account_balance(db, account.code),
        }
        for account in accounts
    ]
    recent = db.scalars(
        select(LedgerTransaction).order_by(LedgerTransaction.created_at.desc()).limit(40)
    ).all()
    transactions = []
    for transaction in recent:
        entries = db.scalars(
            select(LedgerEntry).where(LedgerEntry.transaction_id == transaction.id)
        ).all()
        transactions.append(
            {
                "id": transaction.id,
                "kind": transaction.kind,
                "reference": transaction.reference,
                "memo": transaction.memo,
                "created_at": iso(transaction.created_at),
                "entries": [
                    {"account": e.account_code, "debit": e.debit, "credit": e.credit} for e in entries
                ],
            }
        )
    return {"balances": balances, "balanced": ledger.is_balanced(db), "transactions": transactions}


@router.get("/audit")
def audit_log(
    db: Db,
    _: User = StaffUser,
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        query = query.where(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    entries = db.scalars(query.limit(limit)).all()
    emails = {u.id: u.email for u in db.scalars(select(User)).all()}
    return {
        "items": [
            {
                "id": e.id,
                "actor": emails.get(e.actor_id) if e.actor_id else "system",
                "actor_role": e.actor_role,
                "action": e.action,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "before": e.before,
                "after": e.after,
                "created_at": iso(e.created_at),
            }
            for e in entries
        ]
    }
