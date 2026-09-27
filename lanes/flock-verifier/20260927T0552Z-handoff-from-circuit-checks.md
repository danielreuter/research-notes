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

## Update (06:56Z): the stored build agrees everywhere; your per-set sessions are now check's critical path

- **Built once:** `upstream-build.sh` ran as r20260927-055557-7a65 (5 min on 16 vCPU, rustc 1.98.1). Stored and preserved:
  - `art:5a3f8e47...`: the upstream build, 8.5 MB;
  - `art:b2178129...`: the inputs, 225 MB, your bundle's store/;
  - pinned in `backends/flock/verifier/upstream.json` on `cursor/fast-check-4d78`.
- **It agrees:** check's lean-agreement on it passed 412/412 sessions over all 8 sets, twice (r20260927-060428-6364,
  r20260927-063120-ed83).
- **Suggestion:** with 8 sets at once, the agreement takes 21.6 min, all of it sets 3 and 5, whose ~62 sessions run one after
  another in `agree.py` at about 20 s each. Running a set's sessions in parallel, in `agree.py` or `ci.py`, would bring it to a
  few minutes. It's your code, so I haven't touched it.
- **What check caches:** check reuses an agreement pass when backends/flock/verifier/'s tracked files and the interpreter are
  unchanged. So a flock change outside the verifier costs nothing on a warm machine, and a change to the verifier re-runs it.
  A test enforces that ci.py's scripts import only stdlib and each other. If you add an import, tell me, because the key has to
  widen with it.
