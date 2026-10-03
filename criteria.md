# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The last two tools call a model, and model output is non-deterministic. A single try can fail for reasons that aren't a bug in the loop — a transient rate limit, a truncated response, a phrasing the model fumbles. 4 of 5 catches a genuinely broken loop while tolerating one legitimate model hiccup.Demanding 5 of 5 would make the criterion flaky and force me to chase noise rather than fix real defects.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This branch is pure deterministic code — no model is involved. The same query always produces zero results, and the branch either fires or it doesn't. There is no legitimate reason for it to fail even once. If it fails 1 of 5, that's a real bug, not noise. So the target has to be 5 of 5.

---

## 3. Something about state

Given a query that matches at least one listing, the id of the item passed to suggest_outfit equals the id of session["selected_item"], as shown in the trace — 5 of 5 tries.

**Why this target:**
This is about state plumbing, not model output. run_agent picks results[0], stores it, and hands that same object to the next tool. That's ordinary Python assignment — it either happens correctly every time or the code is wrong. There's no source of legitimate variation here. If the ids diverge even once, the loop is passing the wrong item, which is exactly the failure this criterion exists to catch. So it must be 5 of 5.


---

## 4. Something about the fit card

Given a query that completes all three tools, the fit card mentions the selected item's title and its price — 5 of 5 tries

**Why this target:**
The fit card is model-generated, so the wording will differ between tries — requiring identical text would be both impossible and pointless. What must be stable is a small set of invariants: the card exists, it's a reasonable caption length, and it names the item and its price. Those are controllable through the system instruction, so they should hold every try. 5 of 5 on the invariants rejects empty, off-topic, or overlong cards while accepting the natural variation that makes the card feel human.


---

## 5. Your choice

 Given a query that matches at least one listing and an empty wardrobe, the agent still completes all three tools and returns a fit card — 5 of 5 tries.


**Why this target:**
An empty wardrobe is a fully predictable input, and suggest_outfit is specified to handle it by returning general advice rather than failing. The control flow here is deterministic — the same empty wardrobe should take the same path every time. There's no model-driven variance that could justify a miss. So 5 of 5 is appropriate: if even one try breaks, the empty-wardrobe path has a real hole, which is one of the failure modes this unit asks me to exercise.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
