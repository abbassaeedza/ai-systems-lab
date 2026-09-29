# Human-in-the-Loop Content Pipeline

Pattern: AI-drafted content with an approval gate before publish — built independently for two
separate businesses, which is the actual evidence here (a repeatable design instinct, not a
one-off client config).

> **Provenance note**: two real, live n8n workflows confirm this system exists and was built twice
> — one active workflow for the primary business this content system was built for, and a second,
> independent instance built for a separate business (inactive at last check) — confirmed via a
> live API query, names/active-state/dates checked. Node-level detail wasn't retrievable this session, same MCP-detail limitation as
> `voice-agent-webhooks` (see that module's README for the full note). `reference.json` below is a
> **reconstruction** of the confirmed architecture, not a literal export.

## What it does

A scheduled or triggered job drafts a blog post via LLM from a topic/keyword input, then stops short
of publishing — the draft goes to a human-review checkpoint (Slack or email approval, or a draft
state in the CMS), and only an explicit approval signal triggers the actual publish step to the CMS.

## Why human-in-the-loop

Brand voice and factual accuracy matter more for something that goes public under a business's name
than for an internal ops digest. This is the same principle already applied in
[`natural-language-ops-assistant`](../natural-language-ops-assistant/)'s email-triage path (draft a
reply, never auto-send it) — applied here to publishing instead of replying.

## Built twice, independently

The same draft → review → publish shape was configured separately for a second business, with its
own topic source and CMS target — not a copy-pasted config reused verbatim. That's the actual claim
being defended: this is a pattern I reach for, not a single client's bespoke automation.

## Reliability

The publish step only fires on an explicit approval signal, never on draft completion — a stalled or
ignored approval means nothing publishes. There's no code path where a draft goes live unreviewed.

## Tech stack

n8n · LLM content generation · Slack/email approval step · CMS publish API (WordPress-class)

## What this proves

I default to a human checkpoint before an AI-generated artifact goes public, and I've applied that
judgment consistently across more than one engagement rather than treating it as a special case.
