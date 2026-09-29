# Natural-Language Ops Assistant

Pattern: a chat interface in front of a project-management board that answers natural-language
questions with live data, not a canned summary.

## What it does

A webhook receives a chat message (with rolling conversation context). Before touching any API,
GPT classifies the message into one of six intents — `high_priority_today`, `count_projects`,
`tasks_for_client`, `overdue_tasks`, `task_summary`, or `general_advice` — and a Switch node routes
to the matching branch. Each data-backed branch queries the board via GraphQL, formats the result,
and hands it to a second GPT call with a persona system prompt that argues from the data (flags
risk, recommends a next action) instead of just restating it. `general_advice` skips the board
query entirely and answers from the persona alone.

## Why classify before querying

The alternative — always fetching board data and letting one prompt handle everything — wastes an
API call on every conversational message that isn't actually a data question, and makes the model
guess at structured extraction (which client, which time window) inside a single unstructured
response instead of a small, checkable JSON classification. Splitting intent-classification into
its own call means the routing decision is inspectable (log the JSON, see exactly which branch
fired) rather than buried inside a longer completion.

## How this maps to production

The real deployment adds two more trigger paths onto the same board, both driven by the same
"classify before acting" principle:

- **Inbound-email triage** (Gmail trigger): incoming email is matched to a board item by sender
  domain/email, an LLM call classifies the email as `create` / `update` / `ignore` against that
  item's existing tasks, and only on `create`/`update` does it draft the follow-up — a board update
  comment, a Slack alert, and a Gmail **draft** (not an auto-send) for human review before anything
  goes out.
- **Scheduled daily digest** (cron trigger): pulls the board once a day, has the model produce a
  structured time-blocked agenda (priorities, risks, calls vs. messages vs. deep work, an explicit
  "ignore today" list), and posts it to Slack — a proactive layer on top of the two reactive paths.

All three share the same underlying discipline: classify/decide with a small, structured model call
before taking any action on the board, and keep the model's output-facing action (drafting, not
sending) one step short of fully autonomous where the cost of a wrong action is a real client
communication.

## Reliability

- Empty/malformed input short-circuits to a friendly fallback reply before any API or model call
  runs, rather than erroring downstream.
- The intent classifier's own output is defensively re-parsed (strip markdown fences, `try/catch`
  around `JSON.parse`) with a `general_advice` fallback — a malformed classification never crashes
  the routing switch, it just degrades to the safest branch.
- The email-triage path never auto-sends: an LLM-proposed reply becomes a Gmail **draft**, so a
  wrong classification costs a review click, not a sent email.

## Tech stack

n8n (workflow orchestration) · Monday.com GraphQL API · OpenAI (intent classification + persona
response, two separate calls) · Gmail trigger/draft nodes · Slack

## What this proves

I can design an LLM-in-the-loop system where the model's job is scoped tightly (classify, then
argue from data) rather than asked to do everything in one unstructured call — and I default to
keeping a human in the loop on any action with real-world consequences (a sent email, a client
communication) even when the technical capability to fully automate it exists.
