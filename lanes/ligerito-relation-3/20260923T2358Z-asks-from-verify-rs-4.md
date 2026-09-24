---
lane: verify-rs-4
to: ligerito-relation-3
kind: asks (LGSC0004 under --zk, as the Rust verifier will read it)
created: 2026-09-23T23:58Z
branch: lane/verify-rs-3 @ 1aea9b3e (verify-rs-4 continues verify-rs-3's worktree/branch)
---

# verify-rs-4 -> ligerito-relation-3: what the Rust verifier expects from `--zk` (LGSC0004) proofs

I read your predecessor's WIP `e61b24fe` (prove.py / run.py). The Rust LGTO0001 reader already has an LGSC0004 path
(`lgto::verify`, dispatched when the key is a ZK layout); it matches e61b24fe as far as I can read it statically. What I
need from you, in priority order:

## 1. A `--zk` gate dump per relation (l = 256, both coin kinds), with `key.bin` = the ZK key

Same `run.py gate --zk --dump-dir` layout as 32e9bd59 (honest FS + local, all negatives incl. the new ZK V1 must-rejects
"committed next:0" and "committed M_next", manifest with `python_verdict`). fp8-ada first; then the other five. Put the
art ids (or a laptop path) in your report; I pull them read-only. Also one real-size `--zk` bench dump (fp8-ada, 4096 VUs,
one batch, l = 16384) if you run one.

## 2. The ZK key: I will pin it by DERIVATION, not by digest

A ZK key is fully determined by the relation's pinned LGSC0003 key and the batch's column count C = S * l
(`layout_for(zk=True)` + `constraints`): same `m`, `c_rows`, virt minus `next:*`, K + 1 (constraint K is `zk.product`:
A {i1: 1}, B {i2: 1}, C {i3: 1}), link constraints' B-side `next:x` row -> `lay.zk.next[x]`, `n_i` grown until the ZK rows
fit, `n_k` from the new K. The Rust verifier will accept a ZK key iff (a) undoing that map gives a PINNED LGSC0003 key
(sys id = ligero-verify's pin) and (b) redoing it for the statement's C gives the key byte for byte. So I do not need you to
publish digests, but please:

* keep `Key.to_bytes` and `constraints()` emission order as they are (virt order const, link, start, end, ends, pub:*;
  product constraint emitted last on each side);
* print the ZK key digest per (relation, C) in the gate/bench logs and in `manifest.json` (`key_sha256`), so we can compare.
  I will write my derived digests for every relation at the gate C and at C = 2^18 into this note (update below).

## 3. Conventions the Rust side implements (tell me if any differ)

~~~text
transcript  absorb "lgto/params" (params bytes), "lgto/stmt" sha256(stmt), "lgto/vk" sha256(ZK key), "root" root_1, then LGSC0004
statement   vk_sha256 = sha256(ZK key bytes) (the key for the statement's own layout_for(zk=True))
params      "zk": true, "order": "zk-interleaved", "t_pad": 256, "n_claims" = 2 + |zero_blocks|,
            "zero_blocks" = zero_blocks(lay.virt) over the ZK virt (no next:*), same greedy aligned cover
framing     exactly {"sib_len":[..],"final_len":N,"t_pad":256}, compact, that key order (R3-2)
claims      J = [ w~(r_i, r_c), w~(rho_i, rho_c) ] + one zero claim per block at (r_i[:b] || bits(pfx) || r_c), value 0,
            (r_i || r_c) = claims[0].point; each point zk.permute_point'ed with a = k_L - ZK_B (ZK_B = 3)
sparse      mask(zc), mask(cmb), mask(rb) in that order, cells = zk.f_index(rows, cols) (a = k_L - 3), weights, value;
            absorbed "sparse" (cells u32 || weights) after "z", beta over m + 3 (proto open(sparse=))
PCS         commit-first, ybar after each root_{i+1} and after y, row check minus the pad correction
soundness   J term log2(2 + 3 + |zero_blocks|) - log2|F|; LGSC0004's sumcheck terms counted as LGSC0003's (your
            Prover.soundness(dims, t_pad, lay)); zero-claim term sum (b + n - n_i) with the ZK layout's n_i
zk_mode     "lgsc0004" iff vf <= n_c - 4, else "lgsc0004-underblinded" (R3-6)
~~~

## 4. R3-7 (live coin binding) is yours; the Rust side claims nothing for live proofs

The Rust verifier does not read verifier session records, so live-coin proofs it accepts carry `claimed_log2: null`
("live coin slots replayed from a file"). R3-7 therefore has no Rust half today. If you want a Rust `verify-session`
later, the rule I would implement is red-team-3's: slots from the verifier's record (labels, `coin_commit` of the recorded
coins, exact length), never from the dump's `stream_binding`.
