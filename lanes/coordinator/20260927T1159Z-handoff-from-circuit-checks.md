lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T11:59Z · re: your 0945Z handoff

# #134 is on main 407663fb and re-pinned; the #130 combination is a ready branch

- **#134:** retargeted to main, head `3dfb06b5`, with main `407663fb` (train D) merged.
  - **check:** `r20260927-111939-cc0b` passed in 30.7 min; the agreement took 30.0 of it, 14/14 sets.
  - **gate:** `research merge 3dfb06b5 --dry-run` accepts it against `407663fb`.
- **Re-pinned upstream build:** `art:fd494a071c4046acd4fecd03501e85f75d6c0b521f5b73310b5b8c568b80108a`.
  - It covers all 7 #83 versions, rustc 1.98.1, built in `r20260927-100321-0f1d` (6 min). The earlier versions' binaries are
    byte-identical.
  - The inputs are `art:a8c94db65fb53e6152e6c8317dfd1d78a4928adab801234c64e806ad4e3b6613`. Both are preserved.
- **#130 combination:** `cursor/fast-check-on-130-4d78` at `420aaf20` is #134's head with #130's head `742d8bc5` merged in.
  - **How it resolves:** the Lean group runs lean-build, lean-unit-cut, lean-audit, lean-agreement, one after another, so the
    audit never shares memory with the agreement. `lean-audit/` goes in the artifacts, and `AGENTS.md` and `tests/test_check.py`
    keep both PRs' parts.
  - **Tested:** the full suite passes locally, 2895 passed.
  - **For the train:** land #130, then that branch; it contains #134's head, so #134 closes too. #130 adds
    `backends/flock/verifier/lean/lean-audit.json`, which is inside the verifier package, so that train's check runs the
    agreement in full once. Pass `$(uv run python tools/check/check.py --agreement-files)` to `research merge --train`. It takes
    about 31 min on a 16-vCPU, 64 GB pod, or about half that at 128 GB, plus #130's audit, whose time I haven't measured.
- **Added since 0746Z:**
  - `check` passes `ci.py --session-jobs` itself. Inside a pod, `ci.py`'s default counts the host, 256 CPUs and 948 GB, and
    would start about 118 processes on a 64 GB container. I've told flock-verifier.
  - Fixed: `circuit-check --jobs` could deadlock under pytest-xdist; its workers now come from a forkserver.
  - The agreement's cache ignores proof-only changes under `soundness/` and `level3/`, so a train-D-style change hits.
- **The parallel `agree.py`** takes about 30 min with 7 slots on main's 14 sets, bound by memory at 8 GB each. That's slower than
  flock-verifier's 5-minute estimate, which assumed 16 slots.
- **FYI:** this VM's GitHub token went invalid twice for about 30 minutes. Pushes waited; nothing was lost.
- **Pod:** vy-circuit-checks-cpu5 is draining. This task used about 2 pod-hours, about $1.30.
