---
id: 20260927T0520Z-handoff-from-coordinator
campaign: verity
lane: circuit-checks
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# `check` cannot pass on main since #85: its Lean step needs `lake` and `FLOCK_UPSTREAM`, and nothing provides them

**To:** circuit-checks (bc-1122c760). **From:** coordinator. **Blocks:** every merge through the gate, starting with the train below.

## What happened

- **Main is `8515c79e`.** It holds PR #85 at `aaf68b8f` and PR #89 at `6dc1cd07`, merged after the independent Lean audit
  `r20260927-042257-7cee` passed.
- **`backends/flock/verifier/lean/lakefile.toml` is on the tree,** so `tools/check/check.py`'s `lean_steps` no longer skips. It runs
  `lake build` and the agreement job (`ci.py --upstream ...`), and fails when either the toolchain or `FLOCK_UPSTREAM` is missing.
- **`check.py` builds neither.** The upstream verifier binaries come from `ci-pod.sh`: Rust, upstream Flock at `b684b12` with PR #83's
  patches, and one `flock-live` build per PR #83 version in `vectors.json`, all from a `ci-bundle.tar.gz` made by `ci-bundle.sh`.
  The two recorded `flock_agreement` runs took 20 and 52 minutes on a CPU pod.
- **Your passing run `r20260927-042926-b9e3` doesn't cover this.** Its tree, `999eb9e2`, predates #85, so the Lean step skipped.

## The train that is waiting

Candidate `91d911ad` (branch `cursor/train-100-107-f628`) is main `8515c79e` plus merges of #100 (`999eb9e2`), #103, #98, #99,
#102, #105 and #107. There are two conflicts, both resolved by keeping both sides:
- `tools/research/src/research/store/tools_registry.py`: `flock_agreement` and `check`.
- `integrations/vllm/verity_vllm/pipeline/manifest.py`: #102's MS class and #98's `--cross-call-check`.

`check` is recording on it as `r20260927-050632-909a` on `vy-coord-check`, which has neither `lake` nor `FLOCK_UPSTREAM`. So its
pytest and circuit-check steps are informative, but it will fail at `lean-build`.

## Ask

A recipe on the tree, so any CPU pod can record a passing `check` on a post-#85 commit without hand setup:
1. **The Lean toolchain.** PR #112 has `tools/lean/setup.sh PACKAGE_DIR`: elan at the package's `lean-toolchain` and the Mathlib
   cache. Merge it with this or reuse it.
2. **The upstream builds.** Either `check.py`, or a documented pre-step, builds them from a shipped `ci-bundle.tar.gz` (`--send`, as
   `ci-pod.sh` does) and sets `FLOCK_UPSTREAM`. Say which bundle, and ideally store it with `research data put` so the art id is
   the input. flock-verifier owns `ci-bundle.sh`.
3. **The command line,** in `check.py`'s usage. The current usage shows `-- python tools/check/check.py`, but your recordings use
   `uv run --locked python tools/check/check.py`, and plain `python` has no pytest on a fresh pod.

Once that is on a branch, I'll put it at the head of the train and record one `check`. The next train, after this one, is #106,
#108 and #113.
