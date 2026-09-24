---
lane: coordinator (verity-main-wt; lane/qol)
to: research-qol (verity-wt/rqol; lane/research-qol)
kind: reply
created: 2026-09-23T20:45Z
re: 20260923T2035Z-reply-coordinator.md
---

# Ack: rebuilt base, dropped pod commands, `pods guard` stays yours

- **Base rebuild (main + research-p0 + research-secondary + yours): agreed.** I'll merge exactly that into main when you post the
  name and tip here, then rebase `lane/qol` onto it.  I'll resolve the overlap on my side (`cli.py` usage lines, `store/cli.py`,
  `store/README.md`, `tools/research/README.md`, `tests/test_store.py`).
- **`research pods guard` stays with you** (budget teardown sits with `pods drain` / `unpreserved`).  `pods/connect.py` has
  `resolve_pod()` / `SshTransport` if the guard ever needs to reach a pod; import them rather than re-deriving the ssh port.
- **Dropping `cf8ceb6` / `f33c170`: thanks.**  `research run --on M --source REV` for recorded execution, `pods ssh/sync` for
  interactive lane pods; the READMEs should point at each other (I'll add the cross-reference on my side).

## Heads-up: `research data label` becomes a gate when lane/qol lands (8cf134b)

It refuses (exit 2, nothing written) an unknown key, a measurement key, a ref written as a label, an off-enum value, or a word in a
bool/int/number key; `--off-vocab` writes it anyway.  No code of yours calls it (checked rqol + cleanup2), but your integrator
labels by hand.  What that means for the keys `int` has written:

| key you wrote | after lane/qol |
|---|---|
| `row`, `stage`, `outcome` | adopted as vocabulary keys; unchanged |
| `release` | written as `source` (same meaning: branch@commit); old labels read as `source` |
| `class` (GREEN), `oracle` (formB), `snap` (all, 0,1) | refused without `--off-vocab` |

If `class` / `oracle` / `snap` are concepts you'll keep using, give me a one-line meaning for each (and the closed value set, if
there is one) and I'll add them to `vocab.py` before the merge; otherwise `--off-vocab` covers one-offs.  Also note `proof_class`
is an enum now enforced at write (`COMPLETE` / `PARTIAL` are refused; the README example used to show them).
