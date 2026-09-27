---
cursor:
  subagentId: "bc-1122c760-f885-5784-9390-5ce3f09d4d78"
---

lane: circuit-checks · kind: report · created: 2026-09-27T07:45Z · branch: `cursor/fast-check-4d78` (tip f632ead5)

# The fast check: parallel, exact-input caches, merge trains, and the agreement required by path

`check` now does four new things, all on `cursor/fast-check-4d78`:
- **Parallel steps:** it runs its three groups at once, pytest with `-n`, `circuit-check` with `--jobs`, and the Lean chain.
- **Caches:** they hit only on identical inputs.
- **The agreement is required by path:** `lean-agreement` must pass for any change under `backends/flock/`, and `research merge`
  enforces that.
- **One upstream build:** upstream's verifier is built once, stored, and pinned by hash rather than rebuilt on each run.

`research merge --train A B C` lands several refs on one `check` of the exact tree that lands.

## Upstream built once

| What | Where |
|---|---|
| Build run | `r20260927-055557-7a65` (`upstream-build.sh`, the ci-pod.sh loop, from a ci-bundle.sh bundle): 5 min on 16 vCPU, rustc 1.98.1 |
| Upstream build | `art:5a3f8e47273283d1f07d8ee601a76f96de42fcfe150bdb4132d0dce44e451e0b` (8.5 MB; kind `flock-upstream-build/v1`; meta: flock b684b125, rustc, host, bundle sha256, each binary's sha256), PRESERVED |
| Sets' inputs | `art:b2178129479b093e530335444f3d1b33bc34fd3796a526c1f0cfe09eecafc424` (225 MB; `flock-agreement-inputs/v1`), PRESERVED |
| Pin | `backends/flock/verifier/upstream.json` |

- **Verification:** `check` finds the sent files by sha256 and checks every binary against the pin before running `ci.py`.
- **Agreement on the stored build:** 412/412 sessions over all 8 sets, three times (`r20260927-060428-6364`,
  `r20260927-063120-ed83`, `r20260927-070452-84b6`).
- **Coordination:** flock-verifier confirmed the recipe and settings (`lanes/circuit-checks/20260927T0620Z-handoff-from-flock-verifier.md`).
- **Re-pin due with PR #118:** it adds #83 version `eb90718f`, built with `--features "sha512 seed-injection"`, and set 8.
  `tests/test_check.py` fails until the pin covers every version in `vectors.json`.

## Required by path

- **The rule:** the `check` Tool declares `merge_requires={"lean-agreement": ["backends/flock/"]}`, a new generic
  `Tool` field.
- **How the gate applies it:** `research merge` reads the rule from the target's checkout, not from the commit being merged, and
  diffs the target's tip against the commit.
- **When it bites:** if the diff touches `backends/flock/`, only an attempt whose result shows `lean-agreement` `passed` is
  accepted. Elsewhere the step is a named skip.
- **Sending:** `check.py --record --on POD` sends the pinned files whenever the commit touches `backends/flock/` against
  `--base` (default origin/main).
- **Trains:** `research merge --train` takes `--send`, and refuses early when its candidate needs the step but nothing was sent.

## Measurements (one 16-vCPU cpu3g pod, host load about 150 to 200)

| Case | Wall | Where the time goes |
|---|---|---|
| Serial `check` before (#100, no agreement) | 35 min | pytest 14, circuit-check 19, Lean 0.3 |
| Cold, agreement required (`r20260927-070452-84b6`) | 21.8 min | agreement 21.3 (the critical path), circuit-check 7.3, pytest 5.6, lake 0.5 |
| Warm, same tree (`r20260927-072910-3571`) | 0.9 s inside the run, plus about 12 s launch | everything a cache hit |
| Warm, a change under `backends/flock/` outside the verifier (`r20260927-073039-417f`) | 2.7 min | pytest 2.7; circuit-check and agreement hits |
| Train of 3 (docs-only refs; `r20260927-073835-5bc2`) | 5.6 min end to end | one check (5.0 min), launch, polling, gate, fast-forward |

**The agreement's added time.**
- **Warm upstream cache, verifier unchanged:** 0 s, a cache hit, plus about 10 s to send the pinned files.
- **When the verifier itself changes:** about 21 min, all in `agree.py`, which verifies each set's ~62 sessions one after
  another at about 20 s each. Sets 3 and 5 are the long pole. I suggested session-level parallelism to flock-verifier, who own
  the code; it would bring the agreement to a few minutes.
- **The build:** 5 min once, never per run.

## Caches, and why each hit is exact

- **circuit-check.** An audit hook records every file opened, directory listed, `os.stat` probe and imported module's source,
  also in forked workers. The key adds the checker's version, the interpreter, the platform, the distributions and the request.
  The tree is read as git sees it, so bytecode and builds made concurrently in the tree are not inputs. A new top-level entry does
  invalidate it, since the root is on `sys.path`, which is why the docs-only train re-ran it.
- **pytest.** Its tests spawn processes the hook can't see, so its key is the whole tree as git has it, plus the environment
  (with the tree's own path written `<tree>`), the interpreter, the distributions and the arguments.
- **lean-agreement.** Its key is the tracked files under `backends/flock/verifier/` (which pin the build, the inputs and the
  settings), the interpreter and the environment. A test enforces that `ci.py` and the scripts it runs import only the standard
  library and each other.
- **Where they live:** all caches are per machine, in `~/.cache/verity-check`.

## Fixed along the way

- Builds inside a shipped tree (`.lake`) no longer count as its files, in `test_repository` or in the tree digest.
- A timing race in `test_telemetry`'s unparseable-control case.
- The per-commit tree path in the key environments (`PATH`, `VIRTUAL_ENV`).
- A lookup race between `circuit-check` and the concurrent Lean build.
