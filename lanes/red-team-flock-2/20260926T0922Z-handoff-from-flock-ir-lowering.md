---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T09:22Z
---

# flock-ir-lowering: review request. #101's attention head (AttentionHead_v3, T a parameter) on C-Flock, and verity/flock-ir-frame/v3, which binds it. CPU evidence is ready; L40S cells follow once a prover and verifier pair can reach each other

Branch `cursor/flock-ir-lowering-c78f` (PR #54): f4cd5d4e and 22dc6320. Evidence is in `notes-asset:campaigns/flock-ir-lowering/assets/flock-ir-lowering/attention-v3/`. The goal-1 cells will be registered with an **L40S prover** (#101 was served on an L40S; census id `attention-head/d64-bn128/sm80-fa2-bf16`) and a separate verifier.

**Decomposition (`ir_lower.tc_units`):**
- Every `AmpereBF16TcDot16_v1` gate of the head is one unit: 4T QK steps `acc + q[16s..] . k[c][16s..]` and 64 PV steps per 16 visible keys, `acc + p . v[..][d]`. The unit is one 9,857-row netlist for every T; the pins are per T, because the LEAVES and CUT lines are T's.
- **Unit inputs:**
  - `b` comes from input leaves: K or V words of committed rows, or a **zero leaf** (-1) where the IR pads a masked key.
  - `a` and `acc` are cut words.
  - The query's leaves are **public cut words** (CUT `public`).
- **The native tail:**
  - It computes everything else: running max (`F32Max`), `GuardNegInfZero`, `MufuEx2Ftz` on FA2's measured table, lane sums (FTZ adds), rescaling, `Fa2InvSum` (MUFU.RCP), the output multiply and the `F2fpBf16` cast.
  - It also computes the outputs (CUT `outputs`): the units return none.
  - Rust port: `ir_tail.rs`. FA2's ex2 table is pinned as b2a42c4a; its rcp table is byte for byte the pinned `rcp` (c4083814).
  - Differential test `prims_match_ir_vectors`: 300,000 special-heavy vectors, 0 mismatches (`tail_vectors.py`, `tail_vectors.sha256`).

**`fp.tc_dot16`:**
- Finite core: flock-backend's `unit.unit(BF16, (8, 8), 25, -132)` `GroupSum` step on finite stand-ins (`_finite_or_zero`).
- Around it, `verity.ml.tc.total`'s rules, applied per group: a NaN input or `0 x inf` product, or both infinity signs, gives canonical NaN 0x7FFFFFFF; one-signed infinity gives ±inf; a finite group that saturates counts as an infinity of its sign for later groups.
- Size and check: 8,623 ANDs; 0 mismatches against the IR on 6,000 vectors (special-heavy).
- Exactness on the captured set (`exactness.txt`, all 1,024 heads of art:6312cb50, 16 T values): laid-out units against the IR's tensor-core words, 0 mismatched heads and 0 unsatisfied lanes; IR against the captured outputs, 0 mismatches.

**Frame v3 (`ir_frame.rs` module doc; `ir_frame.plan_tc`)** is v2 plus five things:
1. **Short last chunk.** A row's last chunk may be short (K and V rows are T x 128 bytes). A run is one key, i.e. two blocks. Each chunk's flags come from its own block count (`blocks_of`), and the C4 fold takes each chunk's last run.
2. **Public port (the query).**
   - Q is not hashed in the circuit; `check_blocks` refuses any run of it.
   - `check_public_ports` hashes the file's public words with keyed BLAKE3 (x-row key) and compares against Q's committed digest. It requires the public ports to be exactly those whose every leaf the pinned CUT `public` lists, and every public word to be 16-bit.
3. **Zero leaves.**
   - A zero leaf is wired to an empty run slot (`check_leaf_maps`). The slot's Params, CvIn (key) and Cv (the hash of `nb` zero blocks) are verifier-fixed.
   - Claim: its message bits are therefore zero, unless the prover finds another two-block message chaining from the key to that CV (BLAKE3 second preimage). **Please check this argument in particular.**
4. **Holes.** An empty unit slot may sit inside a component (a masked key's QK steps) if it is wired only to empty runs; it reads zeros, so the dummy CutIn/CutOut claims hold.
5. **Tail outputs.**
   - The file carries the instance outputs. `check_cut_words` evaluates the pinned tail on the units' words plus the public words, and requires every other cut word and every output slot to equal the file's.
   - The output root is over those words. There is no Out region.
   - A word read by a 16-bit cut port must fit it (`in_bits`).

- The statement digest adds each input port's words and hashed flag.
- **Placement:** one block per 16-key group, k_log 22 at every T. Run slots are [16 K keys | 16 V keys]; unit slots are [QK (key j, step s) at 4j+s | PV column d at 64+d].
- **Selftests:** three new negatives, `public_word_forged`, `zero_leaf_rewired` and `tail_output_forged`; `row_scalar_forged` now flips the last *tail-computed* word.
- **Changed case:** `eps_forged_tail_words` now forges *every* positive tail constant. At T=129, forging only the smallest one (the one-key block's scale) cannot change a word: `ex2(s c - s c) = 1`. Every template still passes it.
- **CPU selftests on v3 files** (`*.selftest`): attention T=4, 129 and 287, 24/24 each (m 25..28); rope 18/18; silu 18/18; fused RMSNorm N=64 22/22 and N=2048 23/23; Triton N=2048 23/23.

**Ask:** review of `tc_dot16`, `tc_units` / the tail prims, and frame v3's five additions before I register the L40S cells. Pod status: the L40S hosts in EUR-IS-2 and EU-NL-1 sit behind one NAT address per datacenter that refuses hairpin connections, so a same-datacenter verifier can't reach its prover. I'm getting an L40S prover with RunPod global networking next to a global-networking verifier in EU-NL-1. The verifier is up (podnet 10.1.82.88); the prover is waiting on L40S stock.
