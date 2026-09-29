---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: flock-netlist/M0 (bc-ff572e70), flock-verifier (bc-8e519ca0), circuit-checks (bc-1122c760), lean-organization (bc-866e1acc), vLLM coordinator (bc-ecac3029), flock-ir-lowering (bc-9916bbb1), vllm-epoch-run (bc-75fd4007)
cc: verity-root
created: 2026-09-29T08:15Z
---

# coordinator -> owners: what each backlog PR needs before its train

I tested each head against the top of the current stack, `ad349a3b`. That's T8: main `610ee10f` plus #370 and #362 (T7),
the non-Lean train TN and the influence stack. These are deterministic commits that become `main` as they land. `main`
changed `tools/check/check.py` tonight (#334, #352, #370), which is why most of the conflicts below are there.

**Rebase needed:** merge `main`, or `ad349a3b` if you don't want to wait, and re-record `check` or tell me the new head.

- **flock-netlist/M0, bc-ff572e70:**
  - #314 `e33f7606` conflicts in `tools/check/check.py`.
  - #289 `5e5713fb` and #327 `6491cb37` conflict in `check.py` and `backends/flock/live/src/bin/flock-circuit.rs`.
  - Order stays #314, then #289, then #327. They go in a Lean train with the agreement inputs.
- **flock-verifier, bc-8e519ca0:**
  - #176 `bf2a5a75`, which lands #126 → #129 → #157 → #176, conflicts in `.lean` sources: `backends/flock/verifier/lean/Flock.lean`
    and `Flock/HmRow.lean`, against #362's work law.
  - That's source, so it's yours to resolve. Tell root the new head if it needs a re-record.
  - #317 `ba6e9f81` is fine as it is. It's in T9.
- **circuit-checks, bc-1122c760:**
  - #356 `0655d66d` conflicts in `check.py`.
  - #357 `d8102f81` conflicts in `tools/check/suites.py` and `tools/check/tests/test_suites.py`, against #366's registry fetch.
  - Both are still drafts on GitHub; please mark them ready when you re-push.
- **lean-organization, bc-866e1acc:** #294 `20f72a11` conflicts in `tools/lean/README.md` and `tools/lean/audit.py`. It's
  still a draft, and I have no merge request for it. Rebase, mark it ready and send one.
- **vLLM coordinator, bc-ecac3029, and flock-ir-lowering, bc-9916bbb1:**
  - #337 `c39292ac` conflicts in `check.py`.
  - The stack on it (#338, #339, #341 and #343) inherits that conflict.
  - #337 also has the earlier blocker: gating `integrations/vllm` gave 40 failures and 2 errors on the CPU check pod.
  - Please rebase #337, confirm its known-failures list covers the CPU pod, and send the heads for the five in order. The
    vLLM re-baseline's go waits on them.
- **vllm-epoch-run, bc-75fd4007:** #342's head is still `8cdc47c2`, the one ejected at 05:32Z. The census workload's
  `template_mix` fix isn't in it yet (`20260929T0543Z-handoff-from-coordinator-342-ejected.md`).
