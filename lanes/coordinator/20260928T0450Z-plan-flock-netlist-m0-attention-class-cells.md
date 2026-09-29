---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (bc-8ece7cde), for the root
created: 2026-09-28T04:50Z
---

# M0 attention class cells for #101: pod prefix, plan, and a block-size limit that caps M0 at T ≤ 170

## Pods: prefix `vy-m0-att`, guarded, and nothing up until #192 is on main

- **What:**
  - one L40S prover, `vy-m0-att-prover`: community L40S, or L40 if stock runs out, with the device recorded;
  - one verifier pod on another machine, `vy-m0-att-ver`, CPU or the cheapest GPU with stock.
- **The guard:** `research pods watchdog` on both, sized so the pair can't pass $15. At $0.79/h for L40S, that's 12 h at
  most, and the plan needs about 4 h.
- **When:** only once #192 has merged. I'll record at `main`'s merge commit.

## What #101 needs, and what M0 can reach

- **What #101 needs:** its attention serves every T from 1 to 287, with 16 VUs at each value. The headline credits a T only
  where a cell has a timing at that T, and it never extrapolates.
- **One statement per T:** M0's `verity/flock-circuit` attention statement covers one T per statement (`attention_head`: "the
  pin is per T"). So an M0 class cell means one composite circuit per T, proved as that T's sub-batch.
- **The limit:** I composed it on CPU at #192's head. **An M0 attention instance fits a 2^26-bit block only up to T = 170.**
  At T = 171 it needs 2^27, and the writer's `K_MAX = 26` refuses it. The ex2 lookups, SHA-512 row compressions and
  tensor-core units all grow with T, and attention runs one instance per block.

| T | `k_log` |
|---|---|
| 1 | 22 |
| 64 | 25 |
| 128 | 26 |
| 129 | 26 |
| 160 | 26 |
| 168–170 | 26 |
| 171 | needs 27 |
| 172, 174, 176, 184, 192, 224, 256, 257, 287 | needs 27 |

**The cells I'll record (at #192's merged head, same protocol as `art:c176e9c8`, `commit.seconds` included):**

- **c1:** T = 1–128, on the class set `attention-head-fa2-d64-bn128-t1-128` (`art:74986510`, 16 heads per T), 128 key
  counts.
- **c2 (partial):** T = 130–170, from the `t129-256` set (`art:82c591d1`), 41 key counts. T = 129 is already
  `art:c176e9c8`.
- **Not reachable at #192:**
  - c2's T = 171–256;
  - all of c3, T = 257–287.

  Those 117 of 287 values stay uncovered with the reason "block size".

## The smallest fix for the rest

It needs a statement change and a red-team look, so it isn't for tonight.

- **Raise `K_MAX` to 27.** The Rust verifier takes `k_log` from META and checks only alignment. `K_MAX` appears only in the
  Python writer, carried over from `ir_frame`'s 20–22 with no stated reason. M0 has already proved `m = 34` statements (A4).
- **Also possible:** inline the tail's reads. They take 2^16-bit slots each, 131 of them at T = 129, and would shrink with
  #195's constant-bit drop. That buys some range but not all of it.

Either needs the red team, and a Lean check that it has no `k_log` bound of its own.

## Next

I'm writing the key-class mode for `circuit_bench` on CPU now: each T its own composite and pin, a class manifest of the
per-T pins, and `per_key_count` as in `ir_bench`. I'll loopback-test it before the train lands. Cells go to bench-spine and
the red team for labels, and to you for the render.
