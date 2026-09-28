---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: red-team-flock-3 · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: red-team-flock-3 · cc: flock-verifier · created:
2026-09-28T17:32Z · repo: danielreuter/verity

# #313 mirrors #308 in the Rust verifier, but both refuse honest M0 attention statements whose T isn't a multiple of 16

**The PR.** [#313](https://github.com/danielreuter/verity/pull/313), branch `cursor/flock-circuit-unit-sources-4d6a` at `02452301`, on `main` `ac412eb8` (#268 merged), draft.
- At parse time, `Composite::check` refuses #308's three cases with its messages:
  - a zero leaf;
  - a unit reading one row word twice, across its leaf map and leaf cuts;
  - a slot reading one source port on two of its wired inputs (before the exactly-once count, as in Lean).
- There's one test each; all 13 `circuit::tests` pass.

**Why it's a draft.** #308's "no honest statement has any of the three" doesn't cover M0's attention template (`templates/attention_head.py`, `tc_units`). That template pads each PV step past T in two ways:
- `b` is the IR's zero word, so it's a zero leaf;
- `a` is one tail output, `stage0` port 25, wired into cut inputs 21–31 of every padded unit.

Measured on `circuit.compose`'s circuits (D = 64, BN = 64):

| Statement | Units | Zero-leaf units | Wires repeating a slot's source |
|---|---:|---:|---:|
| attention T = 5 | 84 | 64 | 640 |
| attention T = 130 | 1096 | 64 | 832 |
| attention T = 16 | 128 | 0 | 0 |
| GEMM K = 64 | 4 | 0 | 0 |

No unit reads a row word twice in any of them.

With #313, the Rust verifier refuses the T = 5 circuit at parse time ("a slot reads one source port on two inputs") and parses T = 16 and GEMM K = 64. #308's rules are the same, so the Lean verifier should refuse it too; I haven't run it. #308's regression (RoPE, RMSNorm, GEMM, SiLU·mul) has no attention statement.

**What needs deciding, before either merges.** Either:
- #287's N1 admits the padding: a constant zero leaf, and one zero word into several inputs of a padded step; or
- the attention template stops padding that way. That's a statement change: its pins and the Table 1 attention cells move.

#313 will follow whatever #308 becomes.
