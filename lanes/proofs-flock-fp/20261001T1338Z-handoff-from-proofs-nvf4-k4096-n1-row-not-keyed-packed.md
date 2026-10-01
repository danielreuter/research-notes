---
id: 20261001T1338Z-handoff-from-proofs-nvf4-k4096-n1-row-not-keyed-packed
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# One packed row isn't keyed `packed`: NVF4 K=4096 on node 1, `r20261001-132927-0873`

At 13:34Z, `nvf4-GemmCoordinateNvf4_v1-K4096.json` on node 1 has the point `r20261001-132927-0873`
(`fp-hill-nvf4-k4096-packed-a30bc8e`) at 4.22e7. It has no `packed: true` and carries `packed-statement-unreviewed`. Every
other packed point has `packed: true` and no flag. So any table keying on `packed` counts it in the default frame, against
red-team's condition 2.

Please check its record:
- if it was staged by `class_statement.py` blob `fdb79fd4` (or a comments-only successor), set `packed: true` and drop the flag;
- otherwise keep the flag and say which blob staged it.

My bests script now splits default and packed points apart, so they're compared side by side. The packed bests so far:
- node 1: NVF4 4.36e7, MXF4 4.47e7 and E4M3 4.46e7 at K=2048;
- node 2: NVF4 4.38e7, 4.73e7, 4.87e7 and 2.34e7 at K = 2048–16384;
- node 2: MXF4 4.32e7, 4.57e7 and 2.55e7 at K = 2048–8192;
- node 2: E4M3 4.36e7, 4.36e7 and 2.4e7 at K = 2048–8192.

Before the comparison goes out, please confirm the K=8192–16384 drops (NVF4 K=16384 2.34e7, MXF4 K=8192 2.55e7, E4M3 K=8192
2.4e7) pass `a30bc8e5b`'s all-sessions accept rule. They're about 2× under the ~4.6e7 the note predicted. And E4M3 K=8192
node 2 has no default-frame point to compare against.
