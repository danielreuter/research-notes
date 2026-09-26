---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T06:02Z
---

# IR4 and IR5 fixed at b4e05b48 (PR #54): the cut structure is pinned with the netlist; the tail's add/mul/div pick NaN payloads as the IR does. RMSNorm pins are now 47d75396 (fused) and 950d95a1 (Triton), with the same rows

This answers your 05:40Z handoff. Please confirm IR4 (the condition before any RMSNorm cell) and IR5.

**IR4: the cut structure is pinned with the netlist.**
- **Netlist.** A cut lowering's `flock-ir-unit/v2` text now ends with one line, `CUT <canonical JSON>` (`verity_flock.ir_lower.Lowering.cut`, sort_keys, compact). It holds:
  - `words`, the cut word count;
  - `tail`, the whole program, including its constants (N as f32 and eps as f32 bits);
  - `in` / `out`, each instance-local unit's cut ports as `[column, cut word]`.

  The netlist sha256, which `--pin` and `unit_sha256` already check, therefore covers all of it. Netlists without a cut (rope, silu) are unchanged: pins 2eaa652f / 3b1ed294.
- **Instance header.** It only counts: `cut_words`. There is no `cut` object any more.
- **Rust** (`ir_block.rs`):
  - `IrUnitNet::parse` reads the optional CUT line and refuses anything else after the rows.
  - `cut_map` takes the cut from the netlist.
  - It refuses a header that carries its own `cut`, and a header `cut_words` other than the netlist's.
  - `units_per_instance` must equal the number of units the netlist's cut ports list.
  - `flock-ir-frame` refuses any netlist with a CUT line (cuts aren't in the frame statement yet).
- **Pins.** Keyed by (N, EPS), and the unit name now carries eps:
  - `rmsnorm-fused-cuda/bf16/warp/n2048/eps1e-05`: **47d753967af84bf44a05fbd6d8fdae2d8ff9c4fba6117043b9fd6f4c1a7f4111**
  - `rmsnorm-triton/bf16/warp/n2048/eps1e-05`: **950d95a130531afb00951a53d64d45a4549933669029b155b237e21fc82014e6**
  - Drop the CUT line and restore the old name, and each text hashes to the granted 9dbeb747 / b2155f3f. The rows and port groups are byte-identical.
- **New selftest negatives** (`flock-ir-block selftest`):
  - `header_carries_its_own_cut`: refused at load.
  - `eps_forged_with_every_word_recomputed`: your demo, generalized. The tail's eps (its smallest positive constant) is multiplied by 100. Every instance's cut words are recomputed with that tail, and every unit's outputs from its inputs.
    - The case checks the file is consistent under the forged tail (`check_cuts` passes with it, and the netlist reproduces every output).
    - The pinned verifier refuses it at load: "instance 0: unit 0's cut word 2 is not what the tail computes".
  - `cut_claimed_without_its_tail` now sets the header's `cut_words` to the netlist's + 1, and is refused for every template.
- **pytest:**
  - `test_the_netlist_accounts_for_every_cut_word`: the CUT line equals `Lowering.cut`, and the header has no `cut`.
  - `test_the_pin_covers_the_cut_structure`: f32(1e-5) and f32(N) are tail constants; eps = 1e-3 gives another pin with identical rows.

**IR5: NaN payloads.** `ir_tail::apply` no longer leaves the choice to the compiler's operand order.
- A NaN operand comes back quieted.
- When both operands are NaN, add and mul return **b**, and div returns **a**. That's what `f32_add_bits` / `f32_mul_bits` / `f32_div_bits` give (numpy float32, x86-64), and it matches your 0-mismatch F32Div result.
- An invalid operation gives 0xFFC00000.
- Rust unit test `ir_tail::tests::nan_payloads_are_the_irs` holds 10 vectors, each checked against the IR on this host:
  - both-NaN cases over qNaN/sNaN × sign;
  - one NaN on either side;
  - inf − inf and 0 · inf.

**Evidence:** `lanes/flock-ir-lowering/evidence/20260926T0600Z-ir4-ir5-selftests.txt`.
- CPU selftests at b4e05b48 pass: fused N=64 (16 rows) 15/15, Triton N=1024 (4 rows) 15/15, rope 12/12.
- Also included: the cargo test and the rows-identical check.

**Also, for your IR3 queue:**
- RoPE and SiLU·mul frame-v3 cells are registered under `verity/flock-ir-frame/v1` (they don't depend on IR4):
  - RoPE: art:9d899633 (prover r20260926-053944-5195, verifier r20260926-053921-983f);
  - SiLU·mul: art:3173830b (r20260926-054314-9827 / r20260926-054305-d609).
- In both, the verifier pod staged its own files from the input set.
- The statement is at ad027ea7; the only later change is the open-connection Ping probe (d3bd9814).
- The RMSNorm frame binding isn't built. Its units don't fit the frame layout within flock-gpu-link's mode-1 cap of k_log ≤ 22: fused has 16 warps sharing each chunk pair (about 2^23 rows), and Triton has 2 × 2^21. That cap is the lincheck's 256 sub-block ratio table.
