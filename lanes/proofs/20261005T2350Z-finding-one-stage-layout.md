---
id: proofs/20261005T2350Z-finding-one-stage-layout
campaign: proofs
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: bc-d1cdb9e4-cd78-5229-9ba8-6fea744daf11 (one-stage-layout, for the proofs coordinator bc-8416bc72)
---

# The one-stage audit on the new layout: it runs end to end and refuses a tampered session, after one path fix

Daniel asked this through top on Slack at 4:07 PM PDT on 5 Oct. The question: does `benchmarks/one_stage` still run end to
end on the layout move's settled head `b87eeef64`, and does it still refuse a tampered session?

**Yes.** The move left one break, in `pod.sh`: M0's import roots. With that fixed, A0 accepts the honest session, refuses
all of its negatives, and the Lean verifier refuses the tampered session by name: `lincheck: ConsistencyFailed
(sumcheck-final)`. A second, older gap made the `BIND=1` tampered control vacuous for Lean. It is fixed as well. A third
commit, asked for by the coordinator, makes every Lean-backed negative require Lean's refusal by name, so a refusal for a
missing input can't pass for a refused proof.

* Branch: `cursor/one-stage-layout-95d4`, head `f6640706b`, three commits on `b87eeef64`.
* Nothing under `backends/flock/` changes.

## Runs

All six are recorded `research run`s on a local 4-core VM, CPU only, from 4:25 to 5:07 PM PDT.

Inputs:
* `m0.tar`: a `git archive` of `b87eeef64` (sha256 `7769f782…`). M0 runs from this pinned tree, not from the checkout.
* `lean.tar`: `backends/flock/verifier` at `b87eeef64` (sha256 `a4dbbe96…`).
* The set: the last pre-move A0's captured `rope101` (RoPE d64, n = 1024, sha256 `f1bdbca7…`).

| run | commit | flow | audit | negatives | tampered session, Lean's `why` |
|---|---|---|---|---|---|
| `r20261005-232531-a977` (`art:bd32699602c6c22640db983a6a652a89d59a43a136046a405c61cabc4cd919b3`) | `d3fdebd3f` | A0 `BIND=1 K=16` | accepted, complete | 21/21 refused | `setup: partition: … the verifier's partition object is required` |
| `r20261005-233748-4bcf` (`art:11f462bd9d9953bd282869d004b6ab044d576d74e4e5471408940c3c77c5354c`) | `d3fdebd3f` | A0 `K=16` | accepted, complete | 20/20 refused | `lincheck: ConsistencyFailed (sumcheck-final)` |
| `r20261005-234154-ec01` (`art:4146714d0c3e8a341da654b82385ae65a04640edba18994031cdc1ec9d5b0c23`) | `5b96da663` | A0 `BIND=1 K=16` | accepted, complete | 21/21 refused | `lincheck: ConsistencyFailed (sumcheck-final)` |
| `r20261005-234645-14d7` (`art:50d87b82b8bbd0e2ca781dd13125752ddcdeff9fc532d9d4deafd921e0c0cbac`) | `5b96da663` | A3, RoPE layer 0 (64), `K=16 --draw-file` | accepted, complete | 10/10 refused | n/a |
| `r20261005-235122-722b` (`art:2873b503b78a9d4212938423cb3951f1a65dc1a52465fab926233d9d05552724`) | `5b96da663`, clean | A0 `BIND=1 K=16` | accepted, complete | 21/21 refused | `lincheck: ConsistencyFailed (sumcheck-final)` |
| **`r20261006-000502-e0f3`** (`art:09970d790e980cd74d5c2adcf2ee49e3685d6804b552bb05a59d19470859996f`) | `f6640706b`, clean | A0 `BIND=1 K=16` | accepted, complete | 21/21 refused, none for a missing input | `lincheck: ConsistencyFailed (sumcheck-final)` |

`e0f3` is the run of record for the branch head.
* Its source is recorded clean: tree `b62559a5`, which is `f6640706b`'s.
* It ran from this lane's worktree `/tmp/osl/wt`, with the build dirs in `/tmp/osl/pod-workspace/one-stage`, outside any
  checkout.
* `pod.sh` hardcodes `W=/workspace/one-stage`, so `e0f3` runs `pod.sh`'s steps in its own command: extract the pinned
  tars, check the cached binaries' keys against them, and call `a0.py` with the same arguments.
* Its binaries are byte-identical to `722b`'s: `flock-circuit` `dae76bb5…`, `flock-verify` `be80e68d…`.

In `e0f3`, the Lean-backed negatives refuse by name:

| negative | Lean's refusal |
|---|---|
| `wrong-output-word` | `lincheck: ConsistencyFailed (sumcheck-final)` (M0's verifier and prover: `Lincheck(ConsistencyFailed { which: "sumcheck-final" })`) |
| `public-body-altered-leaf-layer-updated (Lean roots)` | `setup: row out: the rows' b \|\| c do not hash to the header's frame-v3-sha512 root` (registration passes) |
| `draw-altered-after-session (Lean U1)` | `U1: the record's unit draw is not the statement's` |
| `draw-dropped-from-record (Lean U1)` | `U1: the statement carries a unit draw the record does not keep` |
| `instances-not-the-draw (Lean U3)` | `U3: the statement's instances are not the drawn units and their closure` |

The rest refuse by code:
* M0's selftest `prover-ignores-the-draw`: `session aborted: R7: session parameters … differ from the verifier's`.
* Registration: `R1-law`, `R2-program`/`R2-partition`/`R2-population`, `R3-domain`, `R4-leaf-layer`, `R6-window`, `roots`
  and `domains`.
* The draw: `population`, `units-range` and `law`.
* The audit: the `roots` check, and for both C2 negatives "no verifier of record accepted".
* The bindings: `partition`.

The only Lean refusal with a `setup:` reason is the public-body root check, which Lean makes at setup.

What every A0 run does:
* It builds both binaries from the pinned trees: `flock-circuit` with M0's own `60-circuit.sh MODE=build GPU=0`, and
  `flock-verify` with `lake build` (root `FlockVerify`, 96 jobs).
* It stages with M0.
* It passes registration R1-R6 and the public-file and bindings checks before the draw.
* It draws `subset:16` over the partition's 1024 units (partition `ba90a294…`, the pre-move A0's digest).
* It runs one live session. All three verdicts accept: M0's live verifier, Lean's U1-U3 draw checks, and Lean
  `verify --archive` (the verifier of record, 24 s).
* It writes the audit record with its `verity/integrity-profile/v1` profile (`verity/sampled-proofs/one-stage/v1`).

On every tampered session, M0's live verifier and its prover refuse with `Lincheck(ConsistencyFailed { which:
"sumcheck-final" })`.

## Breakages and fixes

1. **`pod.sh`: M0's import roots (`d3fdebd3f`). This is the layout break.**
   * `M0PATH` named `packages/verity/src` and `backends/numerical/python`.
   * Under it, an M0 tree pinned at or after the move fails: `verity_flock.circuit` raises
     `ModuleNotFoundError: No module named 'verity_catalog'`.
   * `m0path DIR` now picks the roots by the tree's layout, keyed on the tracked file `packages/verity/pyproject.toml`.
     Trees pinned before the move, such as the last A0's `m0.tar` `e3c5ba39`, keep their old roots, and `a2`'s `m0b`
     tree uses the same function.
   * What needed no change on the new layout:
     * The Lean side: the package is still `backends/flock/verifier/lean`. Its exe `flock-verify` is rooted at
       `FlockVerify`, and `pod.sh` builds it by exe name, so the `Main` → `FlockVerify` rename doesn't touch it.
     * The driver's own `PYTHONPATH`, the imports of `a0.py`, `a2.py` and `a3.py`, and the `flock-verify` subcommands
       they call (`archive-put`, `draw`, `draw-test`, `verify`).
2. **`a0.py`: the `BIND=1` tampered control never reached Lean's proof check (`5b96da663`). This gap predates the move.**
   * The tampered stage binds its partition, but only the honest stage's partition object and program were handed to
     Lean. Lean refused at setup, and the negative still counted as refused, because its test asks only that Lean not
     accept.
   * The last pre-move A0 has the same refusal (`r20260927-110313-402a`, `art:c49fd9db`).
   * `hold_bound` writes both files beside either stage, and `ec01` and `722b` show the proof refused by name.
3. **`a0.py`: the Lean-backed negatives require Lean's refusal by name (`f6640706b`).** Commit 2's gap went unseen
   because a negative asked only that Lean not accept.
   * `wrong-output-word` now also requires Lean's own verdict to refuse, and not with a `setup:` reason (`lean_refused`).
     Before, it didn't ask for Lean's refusal at all.
   * The `draw-test` negatives require their `U1:` or `U3:` code (`drawcheck_refused`).
   * The public-body negative requires the root check's message ("do not hash to the header's"). Its correct refusal is a
     setup one: `FlockVerify` prefixes everything `buildSession` throws with `setup:`, and the root recomputation is
     among those checks. A blanket "not `setup:`" would fail it.
   * Both predicates accept `722b`'s real refusals. On synthetic verdicts, they reject a `setup:` refusal, a0's "no
     verdict" and "no session recorded" stand-ins, an empty reason, and an unreadable draw.

## Path checks and suites

* `a3.py` with `stage_subset.py` ran end to end (`14d7`).
* `a2.py` was dry-checked only, because it needs a `served.tar` from vllm-serving-commit: its imports resolve and `--help`
  parses.
* `compose_circuit.py`, `stage_subset.py` and `stage_tampered.py` ran directly on the new-layout M0. The composed
  circuit's pin equals the staged one's.
* Suites (`uv run tools/check/suites.py …`) at `5b96da663`: `verity/protocols/verification/sampled_proofs` passed 69
  tests (it is `protocols/one_stage`'s home now), `verity/protocols` 248, and `repository` 45.
* `benchmarks/one_stage` has no suite.

## Notes for whoever runs it next

* `pod.sh` hardcodes `/workspace/one-stage`, and M0's build uses `FLOCK_WORK` (default `/workspace`). On a cloud agent VM,
  `/workspace` is the checkout, so the extracted M0 and Lean trees land inside it. Two things follow:
  * `repository`'s `test_lean_module_roots_are_disjoint` fails on the copies, and passes once they are moved out.
  * A recorded run is marked `dirty: true`. That happened for `4bcf` and `ec01`, whose tree hashes still equal their
    commits'. Excluding the build dirs in `.git/info/exclude` keeps later records clean.
* This affects only an agent VM: on a pod, `/workspace` is not the checkout. Making `W` overridable in `pod.sh`
  (`W=${W:-/workspace/one-stage}`) would let an agent VM run `pod.sh` itself with its build dirs outside the checkout. It
  is left out of this branch, which was asked to stay at one commit for the negatives.
* `pod.sh`'s `m0path` comment names the new layout first, but its test is for the old layout's tracked file. The
  behaviour is right (`722b`'s trace picks the new-layout roots for `b87eeef64`), and only the comment's order reads
  backwards.
* This VM's `/workspace` is one checkout shared by several proofs workers: flock-e2e, one-stage-layout, zk-gateway and
  rec-thm. At 23:17:16Z, five seconds after this lane created its branch, a sibling checked out `cursor/rec-thm-95d4`.
  * Both of this lane's commits (`d3fdebd3f`, `5b96da663`) were therefore made on the local `cursor/rec-thm-95d4`. Its
    first push sent `cursor/one-stage-layout-95d4` still at `b87eeef64`.
  * Fixed without a checkout: the branch ref was fast-forwarded to `5b96da663` and pushed.
  * The local `cursor/rec-thm-95d4` (not on origin) carried the two commits. The coordinator pointed it back to
    `b87eeef64` and detached `/workspace`. This lane's later work (`f6640706b`, `e0f3`) is in its own worktree,
    `/tmp/osl/wt`.
  * A sibling's commit `9ddab1aa8` ("Flock.Guarantees.EndToEnd") was made on the same branch at 23:33Z and reset away at
    23:36Z.
  * Workers on one VM need a worktree each.
