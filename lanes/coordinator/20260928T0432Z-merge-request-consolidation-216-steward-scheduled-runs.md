---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T04:32Z
---

# Merge request: PR #216, the steward's scheduled runs (the nightly `--fresh` Lean audit and the weekly upstream watch)

- **PR:** [#216](https://github.com/danielreuter/verity/pull/216), branch `cursor/steward-scheduled-runs-ac68`, head **`13d884fb1bc08e756df12716fafdcceb87651f7d`**, into `main`. Ready, CPU only.
- **Contents:**
  - `[[run]]` entries in `steward.toml`: daily, or weekly with `weekday`, each launching `research run --on MACHINE …` once per period, with `LAUNCHED`/`RUN-FAILED` lines;
  - the `lean_audit` and `lean_upstream` tools;
  - `audit.py` writes its reports into the run dir;
  - `upstream.py --fetch` clones a missing checkout at the pin.
- **Tests:** 146 passed, 1 skipped (`test_notes`, `test_steward`, `test_upstream`, `test_repository`, `test_cli`, `test_store_prov`, `test_check`).
- **Merges:** cleanly with #149 and #214. No open PR touches `notes.py` or the tools registry.
- **Epoch:** moves no digest.

## After merge: two entries for the live `steward.toml` (yours to add)

```toml
[[run]]
name = "lean-fresh"
at = "10:00Z"
source = "/workspace/steward/verity"
args = ["--on", "MACHINE", "--project", "verity", "--source", ".", "--cwd", "source", "--exclusive",
        "--campaign", "lean-nightly", "--timeout", "7200", "--tool", "lean_audit", "--",
        "python", "tools/lean/audit.py", "--all", "--build", "--fresh"]

[[run]]
name = "lean-upstream"
at = "11:00Z"
weekday = "mon"
source = "/workspace/steward/verity"
args = ["--on", "MACHINE", "--project", "verity", "--source", ".", "--cwd", "source",
        "--campaign", "lean-weekly", "--timeout", "1800", "--tool", "lean_upstream", "--",
        "python", "tools/lean/upstream.py", "backends/flock/verifier/lean/soundness", "--fetch", "--rev", "origin/main"]
```

**The machine is your call.** `--on` needs a registered machine that already exists. I recommend reusing the CPU machine you already run `check` on, at a quiet hour: the fresh audit needs at least 16 GB and takes about 35–45 minutes. The alternatives:
- **A new always-on pod**, such as `research pods create --name vy-steward-lean --cpu cpu3m --vcpu 4 --disk 50 --register --project verity --guard 15`. That is about $6 a day, an ongoing spend that needs the root's or Daniel's go.
- **A pod created per run**, about $0.20 a night. It isn't built, and it would have the steward spend on its own, so I didn't build it.

**Enable `lean-fresh` only after #149 lands:** before #149, `--all --build` can fail on a machine without `elan`.
