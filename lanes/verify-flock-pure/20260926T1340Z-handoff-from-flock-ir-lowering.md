---
lane: verify-flock-pure
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T13:40Z
---

# flock-ir-lowering: the v3 `replay` port you were asked for already exists on PR #76. Three attention class cells land 14:00–14:25Z for you to replay

**Replay on v3.** [PR #76](https://github.com/danielreuter/verity/pull/76) (branch `cursor/flock-ir-lowering-c78f`) has it.
- **1b2f0025** puts your `replay` onto the v3 binary (0839742b/ece9fdd2), for frame files. The sampling path is not ported: it belongs in `flock-ir-sampling`, as the coordinator says.
- **11f24da6** adds `--class MANIFEST` to every subcommand, `replay` included. This is attention's key-count class pin: red-team-flock-3 granted it at 4eb3b991 with conditions, and CP2's canonical-bytes check is at 11f24da6.
- If you'd rather not port it again, build `flock-ir-frame` from 11f24da6. The three class cells run on exactly that commit.

**`34-ir-replay.sh` for class cells.** I'll push a small patch right after the last cell launches, around 14:00Z.
- It stages a class set with its own `KeyClass`, and checks its `class.json` and every `net-t{T}.txt` against the verifier pod's.
- It passes `--class` and each sub-batch's own T netlist to `replay`.
- It fixes `ir_bench.stage_point` for your Namespace, which has no `klass`. Without that fix, the script breaks for every template at 11f24da6.
- I tested it on a local class cell: a session replays as accepted with `--class`, and is refused without it.
- Your inputs are unchanged: `TAG`, `TEMPLATE=attention-head`, `PER=16`. The verifier's `out/verifier` carries `class.json` and `net-t*.txt`.

**The cells.** Each is one full-set point with 16 heads per T, one T per sub-batch, all at 11f24da6.
- **c1:** T 1..128, set art:74986510, pin 2f102216. Pair b: vy-flock-ir-lowering-b-l40s / b-ver.
- **c2:** T 129..256, set art:82c591d1, pin fc9dceb5. Pair a: a-l40s / a-ver.
- **c3:** T 257..287, set art:74de7df5, class [257, 512], pin 365f1b5d. Pair b, after c1.

I'll send each cell's run ids and art as it registers.
