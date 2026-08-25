# Bug Diary

Reproduced failures found while building the Aster & Row support agent, in the order they were found. Each entry follows: reproduction → root cause → fix → regression test.

---

## Bug #1 — Legacy return policy answered as if it were current

**Reproduction**

Ask: *"How long do I have to return a backpack?"*

The agent sometimes answered **45 days**, pulled from `02-returns-policy-legacy.md`, instead of the correct **30 days** from `01-returns-policy-current.md`.

**Root cause**

Retrieval was pure embedding similarity. The legacy and current returns policy documents are extremely close in wording and topic, so the legacy doc frequently scored as high or higher than the current one. Nothing in the retrieval step looked at the `status` or `supersedes` front-matter to prefer the authoritative document.

**Fix**

Added an authority-aware ranking pass after similarity search: documents with `status: active` and no `superseded_by` field are boosted above documents marked legacy/superseded, and superseded documents are excluded from being cited as policy unless the active document is silent on the topic.

**Regression test**

`standard-return-window` — asserts the cited source filename is `01-returns-policy-current.md` and the answer states 30 days, never 45.

---

## Bug #2 — Cancelled order still reported a stale delivery estimate

**Reproduction**

Look up `ORD-1004`, a cancelled order whose record still contained an `estimated_delivery` field left over from before cancellation (August 16). The agent reported that date as if the order were still arriving.

**Root cause**

The order-lookup response passed every field in the order record through to the model, and the prompt didn't tell the model which field was authoritative. The LLM treated the leftover `estimated_delivery` value as still meaningful.

**Fix**

Made `status` the single source of truth for what the agent is allowed to say about an order's progress. For cancelled or returned orders, delivery-estimate fields are dropped from the sanitized tool result entirely before it reaches the model, so there's nothing stale left to reference.

**Regression test**

`cancelled-order-stale-eta` — asserts that for any order with `status: cancelled` or `status: returned`, the response never contains a delivery date and instead states the cancellation/return status plainly.

---

## Bug #3 — Internal order fields leaking into responses

**Reproduction**

Ask a broadly-phrased question about an order (e.g. *"Tell me everything about ORD-1002"*). The raw order object — including customer email, shipping address, internal support notes, and a fraud/risk score — was close enough to the model's context that a sufficiently open-ended prompt could surface one of those fields in the answer.

**Root cause**

The order tool returned the full order record from `orders.json` and relied on prompt instructions ("don't reveal internal fields") to keep the model from repeating them. Prompt instructions are not a security boundary — they're a preference the model can be argued out of.

**Fix**

Replaced the trust-the-prompt approach with a hard customer-safe projection applied inside `order_lookup()` itself, before the result ever reaches the model. Only order ID, status, carrier, and (when applicable) a delivery estimate are included. Email, address, internal notes, and risk score are removed at the data layer, not the prompt layer.

**Regression test**

`order-data-privacy` — asserts that for every order in the fixture data, none of `email`, `address`, `internal_notes`, or `risk_score` ever appear anywhere in the tool result or the final response, regardless of how the question is phrased.

---

## Bug #4 — Silent resolution of a genuine active-source conflict

**Reproduction**

Ask: *"Is the Breeze Tumbler dishwasher safe?"* Two currently-active documents disagree: `11-product-care.md` gives general dishwasher-safety guidance, and `12-breeze-tumbler-product-card.md` gives product-specific guidance that contradicts it for this item. Early versions of the agent picked whichever document ranked slightly higher and answered confidently, with no indication that a conflict existed.

**Root cause**

The retrieval and generation pipeline had no notion of "these two active sources disagree" — it only ever surfaced the single top-ranked chunk per topic, so a genuine conflict looked identical to an ordinary single-source answer.

**Fix**

Added a conflict-detection step that runs when multiple active, on-topic documents give materially different answers to the same question. When that happens, the agent states that the sources conflict, cites both, and recommends human confirmation instead of picking one silently.

**Regression test**

`genuine-active-source-conflict` — asserts the response explicitly names both conflicting sources and does not assert a single unqualified answer.

---

## Bug #5 — Evaluation suite looked flaky, but the agent wasn't the problem

**Reproduction**

Running the full evaluation suite repeatedly produced a different failing case almost every time — `retrieved-prompt-injection` failed on one run, `insufficient-information` on the next, `genuine-active-source-conflict` on another — even though none of the underlying logic had changed between runs.

**Root cause**

This one took several wrong turns before the real cause was found. The first few attempts assumed the LLM's free-text phrasing simply didn't match the expected concept patterns for whichever case failed, and tried to broaden the regex/keyword checks for that specific case each time. That kept "fixing" one run without preventing the next flake.

The actual cause was infrastructure, not logic: the Gemini free-tier API key has a daily quota (20 requests/day), and the evaluation suite alone makes roughly 13+ LLM calls per full run. After several full runs in one session, the quota was exhausted mid-run. When a call hit the quota error, the code correctly fell back to a generic "I'm having trouble generating a response right now" message — but that fallback text obviously doesn't match *any* case's expected concepts, so whichever call happened to land after the quota ran out is the one that failed that run.

**Fix**

Stopped guessing at model phrasing. Isolated a single case and ran it alone to confirm the fallback text was appearing instead of chasing new regex patterns. Added quota-aware handling: exponential backoff respecting the API's `retryDelay`, and a clear distinction in the debug trace between "the model answered and the answer was wrong" versus "the call failed and this is a fallback."

**Regression test**

Not a case-level regression test — this is an infrastructure lesson rather than an agent behavior bug. The fix is captured as an operational note (run the suite once per quota window, or use a paid key) plus the trace-level distinction between real answers and fallback text, so a future flaky run is diagnosable in seconds instead of five rounds of guessing.

This is the failure that was discovered independently of the supplied visible cases — it only showed up from repeatedly exercising the full suite, not from any single case's wording.
