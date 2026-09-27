---
id: 20260927T0552Z-handoff-from-circuit-checks
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: circuit-checks
---

# `check` will require your agreement job for changes under backends/flock/, from one stored upstream build

**To:** flock-verifier (bc-8e519ca0). **From:** circuit-checks (bc-1122c760). **Needs from you:** a yes or a correction on the three
points below. I'm proceeding on this reading meanwhile.

Daniel wants `check`'s `lean-agreement` step required for any change under `backends/flock/`, and skipped by name elsewhere,
without rebuilding upstream for 20 to 52 minutes each time. The plan, on branch `cursor/fast-check-4d78`:

- **Build once.** I run your `ci-bundle.sh` here and build it once on a CPU pod with `ci-pod.sh`'s upstream loop:
  - the tree: upstream flock b684b12, plus `flock-link-b684b12.patch` and `flock-gpu-link-b684b12.patch` from main, plus
    crates/flock-live as a workspace member;
  - the result: one `upstream-<c>` binary per #83 version in vectors.json, stored as one artifact keyed by the flock commit and the
    rustc version.
- **Pin it** in `backends/flock/verifier/upstream.json`: the artifact id and every binary's sha256, plus the inputs artifact (the
  bundle's `store/`).
- **Run it in check.** `lean-agreement` verifies both hashes against the pin, then runs your `ci.py --lean ... --upstream c=BIN
  --inputs`.
- **What I won't touch:** `ci-pod.sh` and `ci-bundle.sh` stay as they are.

**Please confirm:**
1. Are that tree recipe and those patches the ones your bundles used?
2. Should `check` use `ci.py`'s defaults (`--seed 20260926 --fuzz 20`), or do you want other settings?
3. When vectors.json gains a set or a #83 version, re-pinning means rerunning the build and editing `upstream.json`. Is it fine
   that this lives beside your scripts?
