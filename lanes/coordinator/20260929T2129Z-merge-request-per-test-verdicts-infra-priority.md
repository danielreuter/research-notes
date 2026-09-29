---
cursor:
  subagentId: "bc-d66f1270-7ec2-58a6-925c-0b2e1b3c1fd2"
---

lane: coordinator · kind: merge-request · **priority: infra** · from: merge-workflow review (bc-d66f1270) · to: research
coordinator (bc-8ece7cde); cc verity-root, bc-1555924a (MoE test speedup) · created: 2026-09-29T21:29Z · repo: danielreuter/verity ·
about: [#444](https://github.com/danielreuter/verity/pull/444) `cursor/per-test-verdicts-1fd2` at `56487083`, on
[#438](https://github.com/danielreuter/verity/pull/438) `baa24d09` and [#437](https://github.com/danielreuter/verity/pull/437)
`16739c6c`, on `main` `33828711`

# Merge request (infra priority): #444, per-test verdicts and the nightly cold check

Daniel approved it ("cache tests heavily"), and it is top priority. #444's branch carries #437 and #438, so land the three in
one train, in that order (their request: `20260929T2032Z-merge-request-workflow-fixes.md`). #444's head alone carries all
three.

**What it does:**
- **Per-test verdicts:** in the four `parallel = true` suites (flock, numerical, research, vllm), every passing test is kept
  under its module's key, even when its suite fails.
  - The module's key is the suite's key less the sibling test modules its tests can't reach.
  - A re-check after fixing one test module re-runs that module and whatever reaches it, and reuses the rest.
- **TB's case, on the real tree:** #420's fix to `test_store_io.py` changes 39 of the vLLM suite's 354 module keys.
  `test_regression.py` (the MoE cases) keeps its key, so its passes are reused instead of re-running for about 2 h.
- **The backstop:** `check --no-cache` names any cached pass that a fresh run contradicts (`cache_contradictions` in the
  result). The nightly `audit-main` Job queue job (bc-605d7c89) runs it on `main`.
- **Update 21:40Z:** `--nightly` and the steward `launcher` are dropped (head `efa753c8`), because `audit-main` is a Job
  queue job. #444 no longer touches `tools/research`, and no `steward.toml` entry is needed.

**What to know before the first run:**
- **Every suite's pass misses once:** `suites.py` and the guard are in every suite key. Per-test entries start filling from
  the first check after landing; the first check itself reuses nothing.
- **The Lean audit key doesn't change:** `check.py` left it in #437, and #437's own one-time change still applies.
- **Stops keep finished work:** under #438's stop, a suite interrupted mid-run keeps the per-test passes of the tests that
  finished. `--keep-going` is still the way to keep a whole suite's verdict when another group fails.
- **Packs carry the entries:** they are `.json` files under the tests cache, so `--verdicts-in` moves them between pods with
  no change.
- **Scope:** no Lean, no pin, nothing under `backends/flock/`, so no grant is needed and `lean-agreement` doesn't apply.

**Please schedule the nightly** by adding this `[[run]]` entry to the notes repo's `steward.toml`, once #444 is on `main`
and after the render checkout refreshes to `main` at 12:40Z:

~~~toml
[[run]]
name = "nightly-cold-check"
at = "13:30Z"
source = "/workspace/steward/render-src"
launcher = ["uv", "run", "--locked", "python", "tools/check/check.py", "--nightly"]
args = ["--on", "vy-coord-t1"]
~~~

- **Pod:** `vy-coord-t1`, or whichever always-on AVX-512 pool pod you prefer.
- **Cost:** about 2.5–3 h a day, since the MoE tests run cold. That's about $3 a day at L40S prices, under the `vy-coord-`
  line.
- **What a red nightly means:** a `cache_contradictions` entry means a key missed an input. Treat it as a gate bug: stop
  reusing that suite's per-test entries (`--no-per-test`) until it's fixed. Who is told is still open (CI notes open question 6).

**Checks here:**
- `uv run tools/check/suites.py tools/check repository --fresh` at `56487083`: verity-check 74 passed, repository 29 passed.
- The interrupt and sequence tests passed 10 runs in a row.
- The `research` suite, whose steward code changed: result in #444's description. No pod runs on my side.
- Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.
