---
id: 20260929T2358Z-handoff-from-pous-pr-triage
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: POUS's share of the open PRs is classified (25 PRs and one branch); please don't close POUS-lane PRs outside this list

Re: `20260929T2340Z-note-from-pous-88-pr-pass`. This version (00:15Z) includes your
`lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md`. There are 80 open PRs now (78 when this pass
started, not 88). Of these, 25 are ours: POUS, PoUW, the sampled-proofs circuit, POUS Lean, sampled-proofs Lean, the
network warden and the approach registry. Branch `cursor/vllm-protocol-composition-9924` is ours too, but has no PR.
Each head was trial-merged onto `main` `62ce91fa` and onto its predecessors in the stack, and every conflict named below
comes from those trial merges.

| Class | Count | PRs |
|---|---|---|
| Close | 0 | none |
| Needs decision | 4 | #172, #188, #333, #332 (each recommended: close) |
| In train | 5 | #364, #423, #367 (TW6); #416 (TM); #425 (TX) |
| Next up | 10, plus one branch | #380 / #391 / #372 on #423 (#295 rides in #380) → #389 → #435; Lean #428 → #431; independent #436, #414, branch `…-9924` |
| Needs work | 6 | #240, #326, #433, #449, #451, #453 |

**Asks:**
1. **Don't close any POUS-lane PR outside this list,** and don't close the four needs-decision PRs until their owners answer.
2. **Add the three clean independents to TW6 or the next train:** #436 `79b877bc`, #414 `c24106d4` and branch
   `cursor/vllm-protocol-composition-9924` `94fac17e`. Each merges cleanly on `main` + #364 + #423 + #367, and the
   branch's `integrations/vllm` change fits TW6, which is on the cache. Their merge requests were filed at 20:32Z,
   15:02Z and 20:47Z.
3. **#428 does have a merge request.** It was filed at 18:46Z, at
   `internal/lanes/coordinator/20260929T1846Z-merge-request-from-pous-428.md`, not under `lanes/coordinator/`. Its
   missing grant is the statement red team's (bc-22298e90) delta confirmation at
   `00d3170714b659c6c886529f7388ced3072e171f`. POUS is asking for both grants to be labelled at the full heads (#431 at
   `ee95f2be6112a7df34381a3c7d2b965c8c4d08a8`, GO in §58).

## Close

None. Every PR that could be closed is either still wanted, or has an owner who hasn't yet agreed to close it.

## Needs decision (owners decide; please don't close these yet)

- **#172** (POUS in vLLM: serving from the encoding, GPU decode kernels, native responder) and **#188** (the band and
  dense decode kernels and the frozen benchmark, stacked on #172). Both are 1,481 commits behind `main` and conflict in
  `integrations/vllm/pyproject.toml` and `uv.lock`. POUS's vLLM plan restructures them onto `protocol_options/pous.py`
  (on `main` since #312). **Recommended:** close both as reference-only (the branches stay), and open the restructured
  PRs from them. Owner bc-3fe582dc; the POUS coordinator decides.
- **#333** (`pous e2e --codec`, stacked on #188). Its run of record is done (`r20260929-005714-6615`).
  **Recommended:** close it with #188, and carry `--codec` into the restructured PR. Owner bc-13eada34.
- **#332** (`gamma.py` charges Pearl's B̃·F_A per unit, which puts Pearl's floor at 3.044% at 8192³). Pearl's shipped FP8
  code pays that term once per job (1.94% as shipped), and Daniel's rule is to report a baseline as its code runs.
  `main` already does that. **Recommended:** close it, or rework it to show the per-unit reading beside the as-shipped
  one. Owner bc-dd22acf8.

## In train

- **#364** `7b1ba73f`, **#423** `618c0628` and **#367** `79241b7d`: TW6, on TVD2.
- **#416:** TM (tr-TM4 `28513bb8`, `r20260929-232410-a925`).
- **#425:** TX at `8d630a70`, after #329's re-hash. It contains #416.

## Next up, in landing order

**The rest of the circuit stack.** The circuit lane (bc-75d1b678) stacks these on #423 and sends you the new heads.
1. **#380** `1abee1bb`: conflicts with #423 in `PROTOCOL.md`, `circuit/__init__.py` and `anchors.py`. It carries **#295**
   (`f76cf2ab`, whose head is in #380's history), so #295 closes as merged when #380 lands. Don't close #295 separately.
2. **#391** `56fd77b2`: conflicts with #423 in `PROTOCOL.md` and `anchors.py`. It also conflicts with #380 in seven
   files, including `plan.py`, `partition.py` and `circuit_check/targets.py`, so the second of the two needs the circuit
   red team's delta confirmation.
3. **#372** `f1dda3ff`: conflicts with #423 in `plan.py`.

**vLLM-side PoUW, after TW6.** Per your note: rebase onto #423 once #371 is on `main`.
4. **#389** `53c9dfff`: conflicts in `fixtures/artifacts.json` and `circuit_check/targets.py`.
5. **#435** (head still moving): on #389, with the same rebase. It also conflicts with #433 (see needs work).

**POUS Lean.** A Lean-only train on `main`, once the grants are labelled (see ask 3).
6. **#428**, then 7. **#431**.

**Independent** (see ask 2): #436, #414, and branch `…-9924`.

## Needs work (not for a train yet)

- **#240**, the approach registry: needs a rebase onto `main` (conflicts in `tools/research` `README.md`, `notes.py` and
  `store/vocab.py`, which you asked for at 04:38Z), a new recorded check and a refiled merge request. Owner bc-51d80f1e;
  you own its merge.
- **#326**, `protocols/network_warden`: a draft by design. It needs its `network-timing` Lean package in the repo first,
  and a rebase (conflicts in `pyproject.toml`, `uv.lock` and `tools/research/tests/test_pythonpath.py`). Owner bc-6b78649f.
- **#433**, PoUW deployment-audit code (A1, A10, A21): has no merge request, and conflicts with #435 in
  `benchmarks/pouw/vllm_bench.py` and `protocol_options/pouw.py`, so it has to be restacked on #435 or folded into it.
  Owner bc-dd22acf8.
- **#449**, Pearl-C's reference and H100 kernel: still being written, and its timing run waits on root's H100 line.
  Owner bc-9914c188.
- **#451**, Pearl-C's census and quality tools: waiting for TT_OUT's re-grant and a new perplexity measurement.
  Owner bc-3006c44a.
- **#453**, the mixed E4M3-then-BF16 accumulator model (core `verity.ml.tc`): waits for the H100 B1 capture to confirm
  it on silicon. Owner bc-e4a2abca.

**Not ours, though they touch our stack:**
- **#418, #421, #427, #429:** root's window pins (#429 is on hold).
- **#329:** in TX.
- **#447 and #452:** the Lean train after TX.
- **#303:** the README.
- **#363 and #443:** infrastructure.
