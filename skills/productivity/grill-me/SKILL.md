---
name: grill-me
description: Grill me, grill this idea, or challenge my assumptions by relentlessly interviewing the user to reach shared understanding. Use for stress-testing plans, architecture, tech stack choices, product decisions, and vague ideas before implementation; expose risk and overengineering without designing a distant future system.
license: MIT
metadata:
  author: EremesNG
  version: "2.0.0"
  repository: https://github.com/EremesNG/skills
---

# Grill Me

Interview the user relentlessly until you reach shared understanding. Map this as
a **design tree**: every decision branches into the decisions that depend on it.

## Work the frontier in rounds

The **frontier** contains every material decision whose prerequisites are settled.
Ask **all independent, dependency-ready questions** in one numbered round, each
with a recommended answer and a short rationale. In plain-text fallback rounds,
word each so **"yes"** accepts it. Use the user's language and established domain terms.

❓ **Q1** - **<question title>**: <decision, strongest challenge, concrete choices if useful>
➡️ <recommended answer and its trade-off>

---

❓ **Q2** - **<question title>**: <another independent decision, if ready>
➡️ <recommended answer and its trade-off>

Wait for the answers, record decisions and consequences, test contradictions,
and recompute the frontier. A question depending on another open question in
this round belongs to a **later** round. Never bundle dependent decisions.
Keep progress visible with brief checkpoints, not a dump of the entire tree.

## Use the richest question transport

When the question tool supports structure, offer 2–4 real alternatives with a
one-line trade-off each, not yes/no; include a conservative baseline or defer
option when credible. Mark the recommendation with the tool's native recommended flag;
never preselect it. Use previews for comparisons (stack options, snippets, tables),
multi-select for non-exclusive choices, and free text for metrics, values, budgets,
names, and thresholds. Add brief context explaining the evidence behind the question.
Reserve yes/no (confirm) for truly binary decisions and the closure confirmation.
In plain text rounds, keep the ❓/➡️ format above: "yes" accepts the recommendation.

## Facts are your job; decisions are the user's

Inspect available files, plans, tests, tools, and current primary sources for
material volatile claims. Use a sub-agent for fact-finding when available and
permitted; otherwise use tools directly. Never ask users for facts you can look up.
A running investigation is an unsettled prerequisite: block only its descendants
and ask the rest of the frontier now. Mark unavailable evidence and its validation
condition; do not invent certainty. Keep human decisions with their owner; record
explicit delegation rather than silently converting assumptions into consent.

## Keep the interview running

- Prefer a permitted native question tool (`request_user_input`,
  `ask_user_question`, `AskUserQuestion`, or equivalent). Submit the whole round,
  await actual answers, analyze them, and immediately ask the next frontier round
  in the **same execution**. Never end the turn or final-respond after an answered
  round, and never ask "shall I continue?" or require "continue".
- For asynchronous tools, keep one round pending and use native wait/resume.
  A delivery acknowledgment is not an answer; do not poll or send another round.
- Without a permitted question tool, send the round as an ordinary message. On
  the user's reply, include the next round in the same reply, not acknowledgment
  alone. Do not change modes/configuration or create automations to force continuity.
- Stop only when closure is confirmed, the user stops/pauses, an answer is cancelled
  or empty, or only blocked branches remain. A tool error or empty response is not consent:
  leave decisions open, do not retry in a loop. If the tool is unavailable, use the
  ordinary-message fallback; an answerless cancellation pauses the interview.

## Start small; grow only when needed

Scale depth to stakes. Open only branches that can change current scope, design,
safeguards, or commitments; record distant futures as non-goals. Prefer the least complex
sufficient option. Separate **build now**, **prepare cheaply**, and **defer until a trigger**;
simplicity does not waive required security, data integrity, or recovery.
Challenge ideas, not people. Test a rejected recommendation's material consequence
once, then accept and record a coherent conscious trade-off instead of arguing to win.
Do not implement, deploy, purchase, publish, or mutate external systems while grilling.

Refuse false resolution: turn "fast/scalable/secure/cheap" into relevant metrics;
"both" into a primary path or explicit budget; "later" into an owner, trigger, safe
default, and accepted risk; "best practice" into a concrete mitigated risk;
"future-proof" into evidenced demand; "AI will handle it" into evaluation, authority,
fallback, and economics; optimistic dates into scope, capacity, ranges, and contingency.

## When to go deeper

Load only the reference needed by a material branch, not every file up front.

| Trigger | Reference |
| --- | --- |
| Architecture, infrastructure, or concrete technology selection | [Architecture and stack](references/architecture-and-stack.md) |
| Breadth scan: viability, product/domain, quality, security, delivery | [Decision lenses](references/decision-lenses.md) |
| High stakes, evidence gaps, delivery risk, pre-mortem, or closure checks | [Delivery and risk](references/delivery-and-risk.md) |
| User requests a formal blueprint or decision artifact, after confirmation | [Blueprint format](references/blueprint-format.md) |

## Close only with shared understanding

Finish when the frontier is empty, every material branch has a managed disposition,
and no contradiction remains—not merely when all ready questions are blocked.
Present a compact verdict, decisions, trade-offs, and managed follow-ups; ask for
explicit confirmation through the same transport. If rejected, reopen the branches
and continue immediately. Only after confirmation provide the agreed summary or
requested artifact. If stopped early or blocked, label the summary **incomplete**,
list unresolved branches and risks, and never claim closure or start implementation.

Adapted from [mattpocock/skills grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) (MIT).
