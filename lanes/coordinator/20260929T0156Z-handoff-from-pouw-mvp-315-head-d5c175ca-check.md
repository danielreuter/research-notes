---
id: 20260929T0156Z-handoff-from-pouw-mvp-315-head-d5c175ca-check
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# #315's head is `d5c175ca`; its recorded check is `r20260929-015410-5a20` (for the vLLM coordinator)

From the PoUW MVP owner (bc-dd22acf8). See https://github.com/danielreuter/verity/pull/315.

- **Head `d5c175ca`** merges #311's post-D4 head `1a4bd3f0` and current `main` (`b4fd93e9`), with no force-push.
  - The conflicts in `pyproject.toml`, `benchmarks/pouw/pyproject.toml` and `uv.lock` resolved to `main`'s workspace and
    suite tables, since D4 brought #218.
  - `uv.lock` gained `verity-vllm`'s `verity-pouw` edge.
- **Per Daniel's 01:37Z ruling**, PoUW merges as an opt-in, labelled placeholder that is **not auditable yet**. That's
  stated in the PR description, the README and `info()`.
  - The default is `weight_operands = "per-forward"`. That default changed after the GO on `58c3bc49`; see the 0110Z note.
- **Tests on `d5c175ca`:**
  - protocol options: 51 passed;
  - root suite: 18 passed;
  - `protocols/pouw`: 45 passed;
  - `benchmarks/pouw`: 7 passed.
- **Recorded `check`: `r20260929-015410-5a20`**, running in normal parallel mode with a 16 GB swapfile. Its result is in
  the store under that id. The merge status is untouched.
