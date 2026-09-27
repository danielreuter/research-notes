---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T09:55Z · status: final ·
repo: danielreuter/verity · origin: PR #119 (lane/vllm-serving-commit; the served run used 7d4f4b7e)

# A4 run 1 (P4) is served: the files for #101's whole layer 0 without GEMM (12,341 units, partition `46f80472…`)

## The bundle: `art:6719029d87e95d912a7f4eca925ea6e594b4b227505e03302909818147fa32c6`

It's laid out as your `a4.py --served` reads it, with P4's member numbering:

| file | what | sha512 (first 16) |
|---|---|---|
| `registration.json` | `verity/registration/v1`, one record for all members, law `subset:1024`, `window.kind: served` | record digest `c2b8ec641a2a07b5` |
| `index.json` | unit → served identity, per member | |
| `m0-pub-287.bin`, `m0-inst-287.bin` | RMSNorm Triton | `6c83fd00ffd0799c`, `4666d03629d4a7d5` |
| `m1-pub-11480.bin`, `m1-inst-11480.bin` | RoPE | `b193f84a4ddb239d`, `ef62f5908989be52` |
| `m2-pub-287.bin`, `m2-inst-287.bin` | RMSNorm fused | `ec339f9ac4ee86e8`, `e1ca0364c2437469` |
| `m3-pub-287.bin`, `m3-inst-287.bin` | SiLU·mul | `a73f477e831f4038`, `c826e808c0fe0ba8` |

- The `inst` files go to the prover only.
- The same bundle also has `registration-v0.json`, `window.json` (roots, domains, bindings, timings) and `members.json` (the
  byte-match record).
- **Records:** served run `r20260927-092505-bee3` (`art:760da39e…`) and byte-match run `r20260927-094723-d7b3` (`art:85b19a48…`), both
  PRESERVED.

## The registration

- **Built with your `verity_one_stage` at `e569e84a`**, per your A4 rules (`evidence/reg_members_v1.py`):
  - `served_domain` reproduces all 13 domains;
  - `leaf_layer` = SHA-512 of the canonical map from descriptor id to pub-file SHA-512 (`cdebc360…`);
  - **`R.check` returns ok with no codes.**
- **Fields:** `program` `aad113f3…`, `partition` `46f80472…`, `population` 12,341, bases 0, 287, 11,767 and 12,054.
- **`window`:** `run: r20260927-092505-bee3`, `row: llama32-1b…bi-eager` (#101), committer `7d4f4b7e`,
  `served_program` `080f3a50…`, `vllm_v1_run_root` `7adcef49…`, `scope` `model.layers.0.`, `order`
  `verity-vllm/serving-rows/order/v0`.
- **Order, stated exactly:** request, then Program row index, then head. Every template here has one row per token, except RoPE:
  in the prefill step the Program lists layer 0's 256 q rows before its 256 k rows. So RoPE's order is q heads for tokens 0–255, k
  heads for tokens 0–255, then q, k per decode step. That's A2's order, and `index.json` names every unit's row.

## What was checked (1× L40S)

- **#101 with the scheme on:** verdict PASS, program `ccc21347`, manifest `90f81868`, and the `vllm-v1` run root **`7adcef49`,
  unchanged**.
- **Served rows = the capture,** for every captured instance in layer 0:
  - RMSNorm Triton: 256 of 256;
  - RoPE: 64 (the other 960 are other layers);
  - RMSNorm fused: 8;
  - SiLU·mul: 16;
  - all ports byte-equal.
- **Served files = M0's writer:** each member's `m<k>-pub/inst` is byte-identical to M0 `68ae79f2`'s own `write()`, fed the served
  rows, serving's salts and domains, and the global unit indices.
- **Serving overhead:** the hook took 9.2 s (6.5 s reading through openings, 2.7 s hashing on 16 workers).

The salts are in the `inst` files, which sit in R2 custody. That's acceptable for this demo; in production the prover's files never
leave the prover side.

## P6

- **Code ready on CPU:** GEMM shared-row members. The tables and refs follow your grid rule, and both K classes match M0
  `967b8d06`'s shared-row writer byte for byte.
- **It launches** when M0's tables-as-given mode, with the descriptor-id keys, lands and passes that byte-match.
