---
id: 20261001T1148Z-report-from-proofs-mufu-boolean-mufu-tanh
campaign: overnight
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-mufu (bc-e8b97b26-6308-54d5-bdf0-c6c684725c15), copied by proofs
---

CHECKPOINT cc21a7d94 (13:16Z) [open] 6:16 AM PDT: note:proofs/20261001T1315Z-report-from-proofs-arch-serve-session-m0 acted on: posted to owner's serve thread 1790850722.977179; verify 0.256 s / 0.546 s vs 10.46 / 27.42.
CHECKPOINT cc21a7d94 (13:01Z) [open] 6:01 AM PDT: arch serve + bf16 nsys rc 0 on node 1; s4 re-run and pvo-pre3 submitted; 4 packed points shipped on node 2; C6/#667 still open, lander yet to answer top-level's 5:43 post.
CHECKPOINT cc21a7d94 (12:43Z) [open] 5:43 AM PDT: posted top-level's C6/#667/batch message in the lander's 5:40 thread 1790858444.539789.
CHECKPOINT cc21a7d94 (12:31Z) [open] 5:30 AM PDT: C6 unheld (top-level 1790856490.884539); #667 lands on slot d c382dd846 r20261001-120046-c50b; packed points on node 2 (2 shipped, 4 queued). Re-read note:proofs/20261001T1200Z-handoff-from-proofs-flock-fp-packed-frame (updated with GRANT conditions): nothing to act on.
CHECKPOINT cc21a7d94 (12:18Z) [open] 5:21 AM PDT: note:proofs/20261001T1215Z-reply-from-red-team-proofs-554-packed-frame-a30bc8e5b acted on: GRANT with 2 conditions; flock-fp has it in its inbox with the owner's gated yes (busy, resume refused); packed points node 2 first from a30bc8e5b.
CHECKPOINT cc21a7d94 (12:17Z) [open] 5:20 AM PDT: proofs-ir attn branch 3b6653dda passed check r20261001-113404-2729; note:proofs/20261001T1215Z-reply-from-proofs-ir-attn-branch-head-and-check acted on: boolean_fp8 + Attention_v9 handed to circuits (note:circuits/20261001T1220Z), after 7:50 recommended; no proofs PR.
CHECKPOINT cc21a7d94 (12:03Z) [open] 5:05 AM PDT: owner yes on all 5 starred items (1790855684.072569), relayed via 20261001T1205Z handoffs (red-team packed-frame review; bf16-hill s4+nsys, arch serve, verify-overlap preflight at 12:55Z). Inbox note:proofs/20261001T1200Z-handoff-from-proofs-flock-fp-packed-frame acted on: sent to red-team. #638 pin identity restated to owner (1790856094.840319).
CHECKPOINT cc21a7d94 (11:54Z) [open] 4:50 report: goal1 hit 16/16 clean node-1 bests, goal2 hit 37.8s, goal3 open (#638 cleared: lean-audit.json blob a18ab53b identical at 22fe745f and in C6 merged tree; posted 1790855546.393529). Owner asked yes on 5 starred items (1790855605.130489). Node 1 11:55Z: one proofs CPU stage, feeder window closed 11:50Z.
# `MufuTanh_v2`: MUFU.TANH on bits, bit-exact on all 2^32 inputs, 1,049 ANDs

Copied by proofs from proofs-mufu's final message. The original report, `internal/20261001T1145Z-report-from-proofs-mufu-boolean-mufu-tanh.md`,
is in proofs-mufu's own VM store and isn't visible here.

- **Head:** `abc153b55` on `cursor/proofs-mufu-bool-95d4`, on top of `3bf1b6d02`. The commits are `531e21b59` (the
  coefficients and the Definition), `9967b14de` (the circuit-check pin) and `abc153b55` (the tests). No PR.
- **Semantics:** the primitive is pinned in `verity.ml.mufu`. Inside |x| in (2^-8, 8), the value comes from a measured
  RTX 4090 table. Outside it, three rules from exhaustive hardware scans give x, ±1 or 0x7FFFFFFF.
- **Hardware form:** MUFU.TANH uses ex2's interpolator, not a plain table.
  - The squaring step is ex2's truncated square (from column 19, shifted by 2).
  - 51 segments over the eleven binades of |x| in [2^-8, 8), with 2^17 offsets each.
  - Coefficient shift 16. Each segment has its own output exponent, since seven segments straddle a power of two.
  - The coefficients are in `tables/mufu_tanh_quadratic.json`.
- **Cost:** 1,049 AND, 5,408 XOR and 77 NOT. The table read is 947 ANDs, and the identity, saturation, NaN and sign handling
  add 102.
- **Evidence:**
  - All 2^32 words through the circuit: 0 mismatches against `MufuTanh_v1`'s rules plus the measured table (1,344 s on 3
    cores; scratch script, not in the repo). 80,000 random words against the primitive's evaluator: 0 mismatches.
  - The build verifies all 92,274,688 table words of those binades against the coefficients, and the facts the circuit
    relies on. It fails if any is false, and a test confirms a perturbed fit fails.
  - circuit-check: `MufuTanh_v2` passes with 0 failures and 0 warnings: 1,049 ANDs pinned, no mismatch on the lowering or
    on 1,024 word-view vectors, no redundant or dead gates. The six earlier Definitions pass again with unchanged pins and
    digests.
  - `test_boolean_mufu.py`: 52 tests pass, including a slow test over every word of each of the eleven binades.
  - `suites.py`: 21 of 22 pass. The one failure is a verity-vllm test the OOM killer took on its 15 GiB VM, and both of its
    parameters pass when run alone.
- **Relayed:** to circuits for the softcap attention (`lanes/circuits/20261001T1148Z-…-mufu-tanh-head-abc153b55`).
