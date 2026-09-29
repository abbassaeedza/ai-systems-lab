# AI Systems Lab

Clean-room references for AI/agentic systems patterns built and running in production.

Three kinds of module live here, labeled per-module:

- **Sanitized export of a real, deployed workflow** — credentials, client identity, board IDs, and
  execution history stripped, but the actual node graph and logic are unmodified. Where a system's
  real form is a low-code orchestration workflow, exporting the sanitized workflow is more honest
  than reimplementing it as prose or a fake script.
- **Reconstructed from a real, confirmed workflow** — the system's existence, purpose, and active
  state are confirmed via a live API query (name, dates, authorship), but a literal node-by-node
  export wasn't retrievable (older workflow, per-workflow MCP detail access switched off, not
  flipped on for a documentation pass). The architecture described is real; the JSON is an
  illustrative reconstruction, not a literal export — each module's README says so explicitly.
- **Clean-room demo** — a from-scratch reimplementation of a pattern used in a real engagement,
  built against synthetic data, for cases where no exportable artifact of the original exists.
  Labeled explicitly as a demo, never presented as a real client's production system.

## Modules

| Module | Pattern | Type |
|---|---|---|
| [`natural-language-ops-assistant/`](natural-language-ops-assistant/) | Chat, email, and scheduled triggers converging on one intent-classification layer in front of a project-management API | Sanitized real workflow |
| [`voice-agent-webhooks/`](voice-agent-webhooks/) | CRM-integration layer around a third-party AI voice-agent product (lead creation, call reporting, personalized outbound calling) | Reconstructed from real workflow |
| [`human-in-the-loop-content/`](human-in-the-loop-content/) | AI-drafted content with a human approval gate before publish, built independently for two businesses | Reconstructed from real workflow |
| [`ai-payment-reminders/`](ai-payment-reminders/) | Escalating, bucket-transition-idempotent invoice reminder sequence | Clean-room demo |

## What's not here

Real client names, board IDs, credential IDs, webhook URLs, and any captured execution data
(pinned example payloads, real email content, real task names, real invoice data).
