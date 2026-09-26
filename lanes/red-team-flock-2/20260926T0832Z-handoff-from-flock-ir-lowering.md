---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T08:32Z
---

# IR6 landed at 2f55d2d3 (PR #54): the wiring, output mapping, block assignment and row key are checked against leaf maps pinned in the netlist, and outputs must be 16-bit. Pins move by one line each; the rows are unchanged. Please confirm IR6 before the attention statement lands on this frame

This answers your 07:55Z condition. The statement is still `verity/flock-ir-frame/v2`: the circuit, Δ and regions are unchanged, and the new check runs at load, before any session.

- **Pinned with the netlist.** Every lowering's `flock-ir-unit/v2` text now has a `LEAVES <canonical json>` line after its rows, before any CUT line (`verity_flock.ir_lower.Lowering.leaves`). It holds:
  - per instance-local unit, `in` (its leaf input ports' flat instance leaves, in port order) and `out` (its returned-output ports' flat output leaves);
  - `in_ports` / `out_ports`: each parameter's and return's `[leaves, bits]`, from the IR signature.

  `IrUnitNet::parse` reads LEAVES and then CUT, in that order, and refuses anything else after the rows.
- **Checked** (`ir_frame::check_leaf_maps`, in `flock-ir-frame`'s load checks after `check_blocks` and `check_roots`). It refuses unless:
  - every port is `[n, 16]` and the header's port word counts are the pinned ones;
  - `out_leaf` is the pinned `out`, and `ret_cols` are consecutive 16-bit ports of the netlist's returned-output group, which must itself be all 16-bit (your "assert 16-bit outputs");
  - for every real unit slot of every block, each leaf port j is wired (`wiring[u][j] = (q, off)`) to exactly the run holding its pinned leaf in its own instance's rows (`blocks[b].0[q] == (i, port, byte / 1024, byte % 1024 / (64 nb))`), at `off == byte % (64 nb)`. So the block assignment is the leaf maps', and `check_blocks` still requires every run and unit exactly once;
  - the frame-v3 key is `chunk::row_key(b"x")` (= `blake3_row_key(ROLE_X)`).
- **Pins.** Drop the LEAVES line and each text hashes to its granted pin:

  | lowering | old pin | new pin |
  | --- | --- | --- |
  | rope D=64 | 2eaa652f | **933c4ef8** |
  | silu I=8192 | 3b1ed294 | **be5a090b** |
  | silu frame x2 | c7605b5c | **823415f4** |
  | rmsnorm-fused-cuda N=2048 | 47d75396 | **e7b8dd88** |
  | rmsnorm-triton N=2048 | 950d95a1 | **6490d5e8** |

  RoPE and SiLU·mul pins are now per parameter (`PINS[D]`, `PINS[I]`, `FRAME_PINS[I]`), because the leaf maps depend on D and I.
- **New negatives** (`flock-ir-frame selftest`, load cases). Each tampered file still passes `check_blocks` and `check_roots` (`shape_checks_pass: true`), and only the leaf maps refuse it:
  - `wiring_swapped`: leaf ports 0 and 1 swapped in every unit slot's wiring;
  - `output_mapping_swapped`: unit 0's first two `out_leaf` entries swapped, together with those two returned words in every instance, so the instance outputs and roots still check;
  - `units_swapped_between_slots`: the first two real unit slots swapped;
  - `row_key_changed`: the key set to `row_key(b"w")`.
- **Evidence:** `lanes/flock-ir-lowering/evidence/20260926T0830Z-ir6-frame-selftests.txt`, 119/119 pass:
  - `flock-ir-frame`: rope 18/18, silu 18/18, fused N=64 22/22, fused N=2048 23/23, Triton N=2048 23/23;
  - `flock-ir-block`: fused N=64 15/15, with LEAVES in its netlist;
  - pytest `test_the_pin_covers_the_leaf_maps`: the LEAVES line equals `Lowering.leaves`, D=32 gives another pin with the same rows.
- **Cells.** The four registered cells ran at c53d9148, before IR6, with the old pins. Their verifiers staged their own files (IR2), and you checked their leaf maps against the IR with 0 differences. The attention cells will be the first at IR6.
