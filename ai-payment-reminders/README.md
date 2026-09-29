# AI Payment Reminders

Pattern: an escalating, idempotent reminder sequence over outstanding invoices — nudge, then push,
then escalate to a call, without ever double-sending or forgetting a paid invoice.

> **Clean-room demo.** This is a from-scratch reimplementation of a pattern from a real client
> engagement, not an export of that system — no real invoice/client data exists in this repo.
> Synthetic data only, provider-agnostic dispatch (no real email/SMS integration wired in).

## What it does

`reminder_engine.py` takes a list of invoices, classifies each unpaid one into an aging bucket
(`due_soon`, `overdue_1_15`, `overdue_16_30`, `overdue_31_plus`), and — if that bucket hasn't
already triggered a reminder for that invoice — generates a message with escalating tone (friendly
nudge → firm follow-up → urgent → request a call) and dispatches it through a mock channel.

## Why bucket-transition idempotency, not a fixed schedule

A naive version sends "day 3, day 10, day 20" reminders on a timer. That breaks the moment a run is
late, skipped, or re-triggered — either you double-send, or you silently miss a step. Keying off
`(invoice_id, bucket)` instead of a schedule means: re-running the same day is always a no-op (the
bucket hasn't changed), and a resumed run after any gap picks up exactly where the invoice's real
aging is — it can't drift out of sync with reality the way a fixed-interval scheduler can.

## Reliability

- **Paid invoices are excluded before classification**, not filtered after — a race between
  "payment landed" and "reminder cycle ran" can't produce a reminder for a paid invoice.
- **The sent-log is the only state that matters.** No separate "which day are we on" counter to get
  out of sync — the bucket a given day's aging produces *is* the schedule.
- **Re-running the cycle is always safe.** Same day, same invoice state → zero new sends, verified
  in the self-check below.

## Tech stack

Python, stdlib only (`dataclasses`, `datetime`) — no external dependencies, no API keys required to
run.

## Run it

```
python3 reminder_engine.py
```

Runs a self-check: dispatches the first cycle, re-runs the same day (asserts nothing re-sends), then
ages the invoices forward and confirms bucket transitions fire exactly once each while an
already-fired bucket doesn't repeat.

## What this proves

I default to keying reminder/notification state off the actual condition being tracked (aging
bucket) rather than a wall-clock schedule, specifically because schedule-based systems silently
break under the exact conditions (a missed run, a re-run, a late start) that happen constantly in
production — the same idempotency discipline shows up in the CRM↔outbound sync and enrichment
modules elsewhere in this repo.
