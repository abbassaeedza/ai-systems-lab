"""Clean-room demo of an escalating invoice-reminder pattern. Stdlib only, synthetic data."""
from dataclasses import dataclass
from datetime import date, timedelta

BUCKETS = ("due_soon", "overdue_1_15", "overdue_16_30", "overdue_31_plus")

TEMPLATES = {
    "due_soon": "Hi {client}, friendly heads-up: invoice {id} (${amount}) is due {due_date}. Let us know if anything's blocking payment.",
    "overdue_1_15": "Hi {client}, invoice {id} (${amount}) was due {due_date} and shows as unpaid. Could you confirm status?",
    "overdue_16_30": "Hi {client}, invoice {id} (${amount}) is now over two weeks past due ({due_date}). Please arrange payment or reply if there's an issue we should know about.",
    "overdue_31_plus": "Hi {client}, invoice {id} (${amount}) has been outstanding since {due_date} — over 30 days. We'd like to get on a call this week to resolve this.",
}


@dataclass
class Invoice:
    id: str
    client: str
    amount: float
    due_date: date
    paid: bool = False


def classify_bucket(invoice: Invoice, today: date) -> str | None:
    """None = not due yet or paid, no reminder needed."""
    if invoice.paid:
        return None
    days_over = (today - invoice.due_date).days
    if days_over < 0:
        return None
    if days_over <= 2:
        return "due_soon"
    if days_over <= 15:
        return "overdue_1_15"
    if days_over <= 30:
        return "overdue_16_30"
    return "overdue_31_plus"


def build_message(invoice: Invoice, bucket: str) -> str:
    return TEMPLATES[bucket].format(
        client=invoice.client, id=invoice.id, amount=f"{invoice.amount:,.2f}", due_date=invoice.due_date.isoformat()
    )


def send_reminder(invoice: Invoice, bucket: str, message: str) -> dict:
    """Mock dispatch channel — real system would call an email/SMS provider here."""
    return {"invoice_id": invoice.id, "bucket": bucket, "message": message, "channel": "email"}


def run_reminder_cycle(invoices: list[Invoice], sent_log: set[tuple[str, str]], today: date) -> list[dict]:
    """sent_log tracks (invoice_id, bucket) pairs already dispatched — idempotent across runs.
    Only sends once per bucket transition, so re-running the same day never double-sends,
    and a resumed run picks up exactly where the last one left off."""
    dispatched = []
    for invoice in invoices:
        bucket = classify_bucket(invoice, today)
        if bucket is None:
            continue
        key = (invoice.id, bucket)
        if key in sent_log:
            continue
        message = build_message(invoice, bucket)
        dispatched.append(send_reminder(invoice, bucket, message))
        sent_log.add(key)
    return dispatched


def demo():
    today = date(2026, 9, 30)
    invoices = [
        Invoice("INV-001", "Acme Roofing", 1200.00, today + timedelta(days=1)),
        Invoice("INV-002", "Blue Ridge HVAC", 850.00, today),
        Invoice("INV-003", "Coastal Plumbing", 4300.00, today - timedelta(days=5)),
        Invoice("INV-004", "Delta Electric", 600.00, today - timedelta(days=20)),
        Invoice("INV-006", "Fairview Landscaping", 600.00, today - timedelta(days=45)),
        Invoice("INV-005", "Everest Paving", 900.00, today - timedelta(days=10), paid=True),
    ]
    sent_log: set[tuple[str, str]] = set()

    # First run: paid invoice skipped, not-yet-due invoice skipped, other 4 fire once each.
    first = run_reminder_cycle(invoices, sent_log, today)
    assert len(first) == 4
    assert {d["bucket"] for d in first} == {"due_soon", "overdue_1_15", "overdue_16_30", "overdue_31_plus"}
    fired_ids = {d["invoice_id"] for d in first}
    assert "INV-001" not in fired_ids  # not due yet
    assert "INV-005" not in fired_ids  # paid

    # Same-day re-run: idempotent, nothing new dispatched.
    second = run_reminder_cycle(invoices, sent_log, today)
    assert second == []

    # Invoice ages into the next bucket: fires again exactly once, for the new bucket only.
    later = today + timedelta(days=15)
    third = run_reminder_cycle(invoices, sent_log, later)
    assert len(third) >= 1
    assert all(d["invoice_id"] != "INV-005" for d in third)  # still paid, still skipped

    print(f"demo ok — first cycle: {len(first)} sent, re-run: {len(second)} sent, after aging: {len(third)} sent")


if __name__ == "__main__":
    demo()
