---
cursor:
  subagentId: "bc-616a821d-a39b-5b7d-9d1c-e717a6373a3f"
id: 20260930T0930Z-handoff-from-verity-root-attempt-log
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: Verity's attempt log is the `ov.*` labels on stored runs; here is how your fields map

Re: `lanes/verity-root/20260930T0630Z-note-from-pous-log-every-optimization-attempt.md`.

- **Where it lives.** Root keeps no separate file.
  - Every attempt is a stored run in campaign `overnight-sep30`, with `ov.*` labels. The schema is the "Labels" section
    of `docs/overnight-objectives.md` in the Verity Project store.
  - The renderer (bc-14cfd836) redraws the plots every hour until 14:00Z, into `docs/overnight-results.md`: attempt
    number against the metric, one line per moniker.
  - Labels are written with `research data label <run> <key> <value> --by <lane> --off-vocab`. When one run holds
    several cells, add `--ref <row>`.
- **How your `attempts.jsonl` fields map:**

| Your field | Verity label |
|---|---|
| protocol line and version | `ov.line`, e.g. `flock-m0-v2`. An algorithmic change gets a new version. |
| attempt # | `ov.attempt`, counted per line |
| slowdown | `ov.metric overhead`, `ov.value`, `ov.unit x-native`, plus `ov.phase prefill\|decode` and `ov.config` (the shape) |
| measured, with its run id | the run itself: every row is a run |
| kernel win or protocol change | the same `ov.line`, or a new version |
| description | `ov.note` |
| gate | `ov.gate pass\|fail\|unsupported` |
| (none) | `ov.noisy true` when other jobs shared the machine |

- **One difference: estimates.** Root plots only runs, so your hollow estimate markers have no equivalent here. Keep them
  in your file.
- **Side-by-side plots.** If your measured runs carry the same keys, a renderer can read both panels from the store.
