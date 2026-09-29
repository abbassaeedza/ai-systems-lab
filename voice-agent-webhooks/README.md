# Voice-Agent Webhook Integration

Pattern: the CRM-integration seams around a third-party AI voice-agent product, so an inbound or
outbound AI phone call becomes CRM state automatically instead of something a rep has to log by hand.

> **Scope note**: the voice AI itself — the conversation engine, call handling, speech model — is
> built by a separate product team. What this module covers is the webhook/API glue layer that
> makes the voice platform and the CRM behave as one system. Don't read this as "I built a voice
> AI" — I built the integration around one.
>
> **Provenance note**: four real, live n8n workflows confirm this system exists and its shape
> (`voice agent lead creation`, `voice agent end of call report`, `Create voice agent`, `Outbound
> call with dynamic variable` — confirmed via a live API query, active/inactive state and dates
> checked). Node-level detail wasn't retrievable this session — n8n's per-workflow MCP-detail
> access is switched off for these older workflows, and flipping that setting on a live production
> workflow was out of scope for a read-only documentation pass. `reference.json` below is a
> **reconstruction** of the confirmed architecture using standard node types, not a literal export.
> Treat it as illustrative, not as real exported source.

## What it does

Three trigger paths around one voice-agent product:

- **Lead creation** (webhook, fires when a call starts): normalizes caller metadata and upserts a
  CRM lead record keyed on phone number, so an inbound call exists in the CRM the moment it starts —
  not after a human remembers to log it.
- **End-of-call report** (webhook, fires when a call ends): appends outcome, duration, and a
  recording/transcript reference to the same lead record, keyed by call/session ID rather than
  creating an orphan log entry — a rep sees full call context in the CRM without ever opening the
  voice platform's own dashboard.
- **Outbound calling with dynamic variables**: before an outbound call, CRM fields (name, case
  reference, appointment time) are pulled and passed into the voice platform's create-call API as
  `dynamic_variables`, personalizing the agent's script per recipient without a human building
  per-campaign call scripts.

## Why this design

The CRM stays the single source of truth regardless of which side — a human rep or the voice agent —
touched the lead last. That only holds if every voice-platform event (call start, call end, outbound
dispatch) round-trips back into the CRM automatically; a voice AI that doesn't write back into the
CRM just creates a second, disconnected system of record.

## Reliability

- Lead upsert is idempotent on phone number — a caller who calls twice doesn't create two records.
- End-of-call reports attach by call/session ID, so a report always lands on the right lead even if
  many calls happened the same day.

## Tech stack

n8n (webhook orchestration) · CRM API (upsert/update) · Voice-AI platform webhook + outbound-call API

## What this proves

I can build the integration layer around a third-party AI product I don't own, so it behaves as one
system with the CRM instead of two disconnected ones — the same discipline needed to wire any
vendor's webhooks into an existing system of record.
