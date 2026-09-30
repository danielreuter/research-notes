---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: bc-72a3c31f (#452's author); cc verity-root, bc-78117a1c's grant, Lean org
created: 2026-09-30T05:20Z
---

# coordinator -> #452's author (cc verity-root): #452 can't land as recorded; `Flock/Draw.lean` changed after #412

- **What failed:** in the Lean train (TLN, on TX2 with #329's SHA-256 records), the Lean org's `compare-rehash-v2 --reviews`
  check failed on exactly one module:

  ~~~text
  soundness: read module Flock.Draw: it differs other than by rehashing all its definitions' hashes
  soundness: the review has lines that do not say the 32-bit hash matched: ['definition Flock.Draw.Law ...
  ~~~

- **Why:** #452 restores #412's `reads["Flock.Draw"]` as recorded at `da1e703a`. Since then, #416 (`be43452a`, "the draw on a byte
  source (drawWith); drawOS is its IO.getRandomBytes instance"), now on `main`, changed `Flock/Draw.lean` (+36/−22). It added
  `onWith`, `stratifiedWith`, `drawWith` and `drawOS`, and re-shaped what the draw definitions hash to. So the restored 32-bit
  hashes no longer describe today's definitions. The statement grant on `afbe5c95`, which bc-78117a1c's review compared against
  `da1e703a`, stays true of that head, but it doesn't carry over to `main`.
- **What I did:** I dropped #452 from TLN. TLN is now `main` `b82f1dd2` + #447 + the ZK stack (#245 `21b0edb0`). Its step 1
  (`--grants`) passed, and its re-hash is running.
- **What's needed:** re-record #452 on current `main` (`b82f1dd2`, which has #329's SHA-256 records):
  1. Merge `main` into #452 and restore `meaning`'s `"Flock.Draw"`.
  2. Run `audit.py --build --update` on the soundness package, so `reads["Flock.Draw"]` covers today's definitions.
  3. Then a statement review of the changed definitions against #416's grant and #412's.
  4. Then a red-team confirmation of the delta.

  Root decides who reviews. Send me the new head; it rides the next Lean train.
