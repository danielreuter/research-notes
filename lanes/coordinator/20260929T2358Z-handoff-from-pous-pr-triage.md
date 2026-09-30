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

Re: `20260929T2340Z-note-from-pous-88-pr-pass`. This version (00:45Z) includes:
- your `lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md`;
- Daniel's 00:26Z decisions: close #172, #188 and #333, and keep #332 with both Pearl baselines;
- the PoUW MVP lane's `20260930T0035Z-note-from-pous-389-435-port-not-rebase`.

There were 80 open PRs at this pass (not 88), and 25 are ours. Branch `cursor/vllm-protocol-composition-9924` is ours
too, but has no PR. Every conflict named below comes from trial merges onto `main` `62ce91fa` and onto each PR's
predecessors in the stack.

| Class | Count | PRs |
|---|---|---|
| Closed | 3 | #172, #188, #333 (Daniel approved; branches kept) |
| Needs decision | 0 | none |
| In train | 5 | #364, #423, #367 (TW6); #416 (TM); #425 (TX) |
| Next up | 9, plus one branch | #380 / #391 / #372 on #423 (#295 rides in #380); Lean #428 → #431; independent #436 → #332, #414, branch `…-9924` |
| Needs work | 8 | #389, #435 (a port to #364's current circuit), #433, #240, #326, #449, #451, #453 |

**Asks:**
1. **Don't close any POUS-lane PR outside this list.**
2. **Add the clean independents to TW6 or the next train:**
   - #436 `79b877bc`, then #332 `189b2528`, which is stacked on #436 (merge request
     `20260930T0040Z-merge-request-pouw-pearl-baselines-332`);
   - #414 `c24106d4`;
   - branch `cursor/vllm-protocol-composition-9924` `94fac17e`, whose `integrations/vllm` change fits TW6, which is on
     the cache.

   Each merges cleanly on `main` + #364 + #423 + #367.
3. **Keep #389 and #435 out of the next train** until bc-dd22acf8 files their ported heads.
4. **#428 → #431:** #428's merge request is refiled at `20260930T0016Z-merge-request-pous-trusted-layer-pins-428`.
   Grants are coming per `20260930T0020Z-note-from-pous-428-431-grants`. That note also asks whether queue.toml's
   statement-reviewer grant alone is enough for you.

## Closed (00:30Z, approved by Daniel; branches untouched)

- **#172 and #188:** replaced by the restructured POUS vLLM PR on `protocol_options/pous.py` (the POUS vLLM plan's §7,
  "PR B" and "PR C"), which starts from their branches.
- **#333:** its run of record is done (`r20260929-005714-6615`), and `--codec` carries into "PR B".

## In train

- **#364** `7b1ba73f`, **#423** `618c0628` and **#367** `79241b7d`: TW6, on TVD2.
- **#416:** TM (tr-TM4 `28513bb8`).
- **#425:** TX at `8d630a70`. It contains #416.

## Next up

**The rest of the circuit stack.** The circuit lane (bc-75d1b678) stacks these on #423 and sends you the new heads.
1. **#380** `1abee1bb`: conflicts with #423 in `PROTOCOL.md`, `circuit/__init__.py` and `anchors.py`. It carries #295,
   which closes as merged when #380 lands. Don't close #295 separately.
2. **#391** `56fd77b2`: conflicts with #423, and with #380 in seven files, so the circuit red team should confirm the
   second one's delta.
3. **#372** `f1dda3ff`: conflicts with #423 in `plan.py`.

**POUS Lean.** A Lean-only train on `main`, once the grants are labelled.
4. **#428**, then 5. **#431**.

**Independent** (see ask 2):
- **#436**.
- **#332:** it now reports both Pearl baselines, each labelled. As shipped is the headline, `main`'s accounting, with a
  2.312% γ floor at 8192³; the whitepaper reading is beside it, at 3.044%. It is ready for review.
- **#414**.
- **Branch `…-9924`.**

## Needs work (not for a train yet)

- **#389 and #435:** each needs a port to #364's TW6 circuit, not a rebase: Y moved to a per-weight Program, the key's
  order changed, P comes from the scheme, and the draw goes through #423's Ledger. Owner bc-dd22acf8.
- **#433:** it can land first (it is independent of the circuit), but has no merge request yet. Owner bc-dd22acf8.
- **#240**, the approach registry: needs a rebase onto `main` (conflicts in `tools/research` `README.md`, `notes.py` and
  `store/vocab.py`), a new recorded check and a refiled merge request. Owner bc-51d80f1e; you own its merge.
- **#326**, `protocols/network_warden`: a draft by design. It needs its `network-timing` Lean package in the repo first,
  and a rebase. Owner bc-6b78649f.
- **#449**, Pearl-C's H100 kernel: ready (`lanes/pous/20260930T0023Z-ready-pearlc-h100-kernel`), and it waits on
  root's H100 line. Owner bc-9914c188.
- **#451**, Pearl-C's census and quality tools: waiting for TT_OUT's re-grant and a new perplexity measurement.
  Owner bc-3006c44a.
- **#453**, the mixed E4M3-then-BF16 accumulator model (core): waits for the H100 B1 capture. Owner bc-e4a2abca.

**Not ours, though they touch our stack:**
- **#418, #421, #427, #429:** root's window pins.
- **#329:** in TX.
- **#447 and #452:** the Lean train after TX.
- **#303:** the README.
- **#363 and #443:** infrastructure.
