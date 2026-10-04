---
id: 20261004T2202Z-report-relay-docs-p3-instantiation
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/p3-instantiation.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/p3-instantiation.md`, sha256 `fe8f6169309a435e5ddb7335873984fa3ce2cc87498937322e262e5c41314603`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P3 instantiation: concrete H and P

27 Sep 2026, revised 16:45Z, for workstream 1 (secure end to end; performance ignored). It targets the §2c operating point of the [P3 scheme](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md): B(220, 12), 64 KB labels, P tweakable per (segment tag, layer, node), strict Δ = 300 µs, and a CPU-core or GPU-core adversary.

The revision replaces the 15:50Z sponge H, which the pilot broke (`lean/submissions/sponge-dense/NOTES.md`, `dense_two_labels_from_one_state`). `docs/p3-gpu-measurements.md` has not landed, so GPU costs use `internal/prior-gpu-notes.md` §1–2. CPU latencies are measured (§3).

**Summary.**
- **H: an overwrite chain on a double-width permutation.**
  - Each call puts one parent next to the chaining value: `(r_j, h_j) = Π_2(B_j ‖ h_(j−1))`.
  - It keeps the (m + 512)-bit part h_j and drops the m-bit part r_j.
  - The key is r of the final pad call.
- **P:** a tweakable 10-round Feistel with SHAKE256 (FIPS 202) round functions, keyed by the tweak.
- **Π_2:** the same Feistel construction, untweaked, 2m + 512 bits wide.
- **Why this mode.** A chaining value is m + 512 bits and yields only its own row's key, because recovering an absorbed parent from it needs the dropped r_j. Anything that reveals a parent and also shortcuts the row is a whole call state of 2m + 512 bits, which is more than the two labels it yields. The XOR sponge and both feed-forward modes fail this test (§1). A state game over all three modes agrees.
- **Timing.**
  - One Π_2 call is 9,650 sequential Keccak-f calls: at least 480 µs on a CPU core, and 2.4 ms measured.
  - One P call is at least 240 µs.
  - Inside Δ the adversary finishes at most one P call and no recomputed level. The certified depth is 10.
- **Cost.** About 24,000 SASS/B: roughly 150× at prefill and 3,800× at decode batch, against the 2× budget and the spec's 5.8×. That is 0.7 GB/s of decode on one H100, and 1.8× the broken sponge.

## 1. H: an overwrite chain on a double-width permutation

**What must hold.** Call a *checkpoint* any value from which a row's key can be finished without the parents absorbed before it.
- (i) No checkpoint smaller than two labels may reveal an absorbed parent.
- (ii) No value may be linear in a parent (a masked copy of it) and also be a checkpoint. This is the linear-keys lesson (`internal/efficient-crypto/candidates/linear-keys.md`, V3): "the adversary stores the m-bit pre-image, which is still an equation". It is the same factor 2 as in Chen–Tessaro (CRYPTO 2019).

**Why the candidates fail.** `x_j = s_(j−1) ⊕ (B_j ‖ 0)` below is the permutation input; the "prefix" means `s_(j−1)`, which is recomputable from the public IV when the newer parents are known.

| Mode (width m + 512) | Checkpoint that reveals a parent | Result |
|---|---|---|
| Sponge, s_j = π(x_j) | s_q: walk back with π^(−1), walk forward from the IV, extract the gap | **broken** (pilot) |
| Feed-forward, `s_j = π(x_j) ⊕ s_(j−1)` | s_j: from the prefix `s_(j−1)`, `B_j = π^(−1)(s_j ⊕ s_(j−1)) ⊕ s_(j−1)` | **broken** |
| Miyaguchi–Preneel, s_j = π(x_j) ⊕ x_j | the pre-image x_j: it is a checkpoint (s_j = π(x_j) ⊕ x_j), and `B_j = x_j ⊕ s_(j−1)` with no call | **broken** on P3's rows (below) |

Miyaguchi–Preneel does stop gap-closing between two states, since x ↦ π(x) ⊕ x is one-way. But the adversary stores x_j instead: it is m + 512 bits, an equation in B_j, and a checkpoint.

**The fix** is to make the only checkpoints either one-way outputs or values of at least two labels. That forces a permutation wider than parent plus chaining value, with part of its output dropped.

**Specification.** Integers are little-endian. A label is 220 components of 298 bytes: m = 65,560 B, w_c = 2,384 bits. The designer should confirm this width.

~~~text
tag_s     = salt (24 B, drawn by the verifier after W is committed) || u64(s)          32 B
Feistel10 = (L, R) -> (R, L xor F_i(R)) for i = 1..10; inverse (L, R) -> (R xor F_i(L), L) for i = 10..1
Pi2       = Feistel10 on 2m + 64 B = 131,184 B (halves 65,592 B), F_i(x) = SHAKE256(0x48 || u8(i) || x)[0 : 65,592]
P_T       = Feistel10 on m = 65,560 B (halves 32,780 B), F_i(T, x) = SHAKE256(0x50 || u8(i) || T || x)[0 : 32,780]
            T = tag_s || u8(layer) || u16(v)                                                 35 B
H(tag_s, layer, v, parents):
  h_0 = "pous-p3-v1-H" || tag_s || u8(layer) || u16(v) || u8(npar), zero-filled to m + 64 B   (no call)
  B_1..B_npar = c_{v-1}, ..., c_{v-npar}  (newest first, npar = min(v, 12));  B_pad = 0x01 || 0..0 || 0x80  (m B)
  for B in (B_1, ..., B_npar, B_pad):  (r, h) <- Pi2(B || h)   with r = first m B, h = last m + 64 B
  key = r of the B_pad call
c1_v = P_(tag_s,0,v)(W_v xor H(tag_s,0,v, c1_par(v)))
c2_v = P_(tag_s,1,v)(transpose(c1)_v xor H(tag_s,1,v, c2_par(v)))
~~~

This is Merkle–Damgård over the truncated permutation Π_2, which is the same as an overwrite-mode sponge with rate m and capacity m + 512. The header in h_0 fixes the length, the pad call always comes last, and the key is a dropped rate, never a chaining value.

**Why no stored item smaller than two labels yields two labels.**
1. **The checkpoints** are h_j (m + 512 bits), and whole inputs, outputs or Feistel states of one call (2m + 512 bits). A half-state of the Feistel is not a checkpoint: the other half is a function of `h_(j−1)`, i.e. of the prefix.
2. **h_j reveals no parent.** Recovering B_j or `h_(j−1)` from h_j, even given `h_(j−1)`, needs either a Π_2^(−1) query on (r_j ‖ h_j) with the unknown m-bit r_j, or a forward query on the unknown B_j. That is at most Q · 2^(−m). So there is no backward walk and no gap to close: h_j yields exactly its own row's key.
3. **Values that reveal a parent** are a call's input or output, or the Feistel half-states `R_t = L_(t−1) ⊕ F_t(R_(t−1))`. These are the only intermediates linear in a parent (check (ii)).
   - A half-state is a masked parent that needs the prefix, so storing it is storing the parent with no shortcut.
   - A whole call state costs 2m + 512 bits for the parent plus its row: dominated.
   - The key r and every h_j are Π_2 outputs, nonlinear in the parents.
4. **Freshness, the step that broke.** A label is learned from:
   - its own row's final query, or its P_T query;
   - a Π_2^(−1) answer, whose query must contain a dropped r_j, i.e. m bits stored or guessed;
   - or a prediction.

   So the ex post facto charge stays about one label's worth per recovered label.

**The state game agrees** (`internal/p3-instantiation/overwrite-state-game.py` and `.log`). It extends the pilot's `state_game*.py` to three modes and to band rows with the extra P call. It asks, for each missing pair of labels, for the cheapest single item that gets both within D rounds when storing either one of them does not.

| Mode | Dense rows, B ≤ 20, D ≤ 6 | Band k = 4 (B = 14) and k = 6 (B = 18), D ≤ 10 |
|---|---|---|
| Sponge | a state of 1.06 labels is worth 2, at every size | same |
| Miyaguchi–Preneel | none (geometry: the recomputed parent's row is as short as the checkpoint's remainder) | **the pre-image x, 1.06 labels, is worth 2** at D = 3–5 (k = 4) and D = 4–7 (k = 6) |
| Overwrite chain | none | only a whole call state (2.06 labels) is worth 2: dominated |

**Other points.**
- **Absorption order.** Newest-first still costs the honest decoder nothing. Every level costs at least 3 calls (`p3_level_ge_three`): Π_2(oldest parent), Π_2(pad), and P.
- **Cheaper variant.** Absorbing 3–4 parents per call, on a permutation (s+1)m + 512 bits wide, does 20–25% less work. A whole call state then costs s + 1 labels plus 512 bits for s + 1 labels, so it is still dominated.
- **Secondary option: lane-first SHA-256 with full re-absorption** (fix (b)). It meets (i) and (ii): Davies–Meyer lanes and a 64-byte pre-image per lane. But at 64 KB it is about 45× this chain's cost.

## 2. P: a tweakable 10-round Feistel from SHAKE256

- **Assumption.** SHAKE256 is a random oracle. Then each F_i(T, ·) is an independent random function for each (i, T), and each P_T is an independent Feistel network.
  - The keyed 10-round Feistel is indifferentiable from an ideal cipher (Dachman-Soled–Katz–Thiruvengadam, ePrint 2015/876, `O(q^12/2^n)`).
  - Per tweak, it is indifferentiable from a random permutation at 10 rounds (Dai–Steinberger, ePrint 2015/874) and at 8 (ePrint 2015/1069, `7.4 · 10^6 q^8/2^n`).
  - The halves are 262,240 bits, so every bound is negligible at q = 2^128.
- **Rounds.** 10 is the least count with two independent proofs; 14 (Holenstein–Künzler–Tessaro, STOC 2011, arXiv:1011.1264) adds a third for 40% more cost. Π_2 uses the same argument, untweaked.
- **The tweak** adds 35 bytes per round-function input: under 0.1% at 64 KB, and about 1% overall at 1 KB.
- **If an ARX mixer is kept (heuristic).**
  - The tweak becomes the round key of a 5-round iterated Even–Mansour cipher with the trivial key schedule: `P_T(x) = k ⊕ π_5(k ⊕ ⋯ π_1(x ⊕ k))`, with k = SHAKE256(0x4B ‖ T)[0:m].
  - That is an ideal cipher when the π_j are ideal (Dai–Seurin–Steinberger–Thiruvengadam, ePrint 2017/042). Light mixers are not ideal (attack 6).
  - It costs about 30–40% more.
- **The multi-stage caveat.** Indifferentiability does not compose in storage games (Ristenpart–Shacham–Shrimpton, ePrint 2011/339; Mittelbach, ePrint 2013/286, covers only "unsplittable" games).
  - The Lean proof therefore stays in the two-permutation model (the pilot's `p3SpongeModel`, with Π_2 in place of Π).
  - Replacing Π_2 and P_T by Feistel-SHAKE is the named heuristic step.
  - What supports it: every data path is full width, and each 1600-bit SHAKE state is a function of a half that the computation also carries.

## 3. Timing at strict Δ = 300 µs, one CPU core

**Measured** on this VM (Intel Xeon, family 6 model 207; dependent chains; `internal/p3-instantiation/cpu-latency-bench.c`):
- Keccak-f[1600]: 244 ns;
- BLAKE3 compression: 107 ns;
- SHA-256, scalar: 199 ns. The VM traps SHA-NI, so SHA-NI uses the published 25–35 ns per block.
- Daniel's ARX chain runs at 28.7 ns here, against 58 ns on his Xeon 8470.

**Sizing floor:** Keccak-f ≥ 50 ns. A GPU thread takes 1–2 µs per Keccak-f call, so the CPU sets the step.

Every recomputed level costs at least Π_2(oldest parent) + Π_2(pad) + P, and the last level may be a lone P call. So the level count is `d = ⌊(Δ − t_P)/(2t_(Π_2) + t_P)⌋ + 1`. The certificate covers d ≤ 10.

The Lean accounting, `levels D 3` with D counted in the fastest calls, is more conservative and gives the same d at 64 KB.

| Primitive | Parallel speed-up? | Call latency, 64 KB labels | d | Call latency, 1 KB labels |
|---|---|---|---|---|
| **Π_2 / P_T: Feistel-10, SHAKE256** | none (serial sponge) | 483 / 242 µs floor; 2.4 / 1.2 ms measured | **1** (only a ready-key P call) | 7.5 / 3.8 µs floor |
| Feistel-10, SHA-256 (SHA-NI) | output lanes | 260–360 / 130–180 µs | 1 | 5–7 / 2.5–3.5 µs |
| Feistel-10, BLAKE3 | tree chunks | 18–50 / 9–25 µs | 3–7 | 8–22 / 4–11 µs |
| ARX butterfly (§2c, heuristic) | every stage | about 33 / 16 µs per core; half that per SM | 4 per core, 7 per SM | 0.3 / 0.15 µs |

- **At 64 KB, a recomputed level takes at least 2Π_2 + P ≈ 1.2 ms at the floor**, 4× Δ. Reaching d = 10 needs Keccak-f at 1.3 ns or less, 40× below the floor.
- **8 KB labels** keep d ≤ 2 at the floor (Π_2 ≈ 60 µs, P ≈ 30 µs).
- **1 KB labels** need about 6 extra blank Π_2 calls per key (d ≈ 5).
- **Serial sponges hold their latency;** ARX butterflies and BLAKE3 trees get faster with more cores.

## 4. Isolation and the verifier

- **Verifier.**
  - It computes vk from its own Enc(W, salt).
  - vk is the root of a SHA-256 Merkle tree: leaf `= SHA256(0x00 ‖ tag_s ‖ v ‖ c^(2)_v)`, node = SHA256(0x01 ‖ ℓ ‖ r).
  - An answer is the 64 KB block plus about 21 × 32 B of path.
  - Binding is plain collision resistance, a single-stage property, so the narrow-state issue does not arise.
  - Per-block digests (0.05% of C) are an alternative.
- **Isolation.**
  - The deadline does not locate data: a host-DRAM attacker was only 5 µs slower.
  - With the host CPU in the adversary's compute, P3 certifies what the whole server holds.
  - Pinning that to HBM needs the bulk bandwidth audit. Its off-HBM tolerance (2.2–2.5%) plus γ = 1.83% fits the 5.26% margin with about 1 point to spare.

## 5. End-to-end decode cost

**Pricing** follows `prior-gpu-notes.md` §1.
- Keccak is single-pipe: R_dec ≈ 1 + 0.158 I and R_pre ≈ 1.1 + 0.0063 I, for I SASS per decoded byte.
- Keccak-f is about 6,000 SASS.
- Per label per layer: 13 Π_2 calls at 9,650 Keccak-f each, plus 1 P_T call at 4,830.

| Variant | SASS/B | Decode (b ≤ 8) | Prefill | d at the floor |
|---|---|---|---|---|
| **Recommended: 64 KB, overwrite chain, SHAKE-Feistel** | ≈ 23,800 (20,000–30,000) | ≈ 3,800× | ≈ 150× | 1 |
| same, 3–4 parents per call | ≈ 18,500 | ≈ 2,900× | ≈ 120× | 1 |
| 8 KB labels, same primitives | ≈ 23,800 | ≈ 3,800× | ≈ 150× | ≤ 3 |
| 1 KB labels, plus 6 blank calls | ≈ 34,600 | ≈ 5,500× | ≈ 220× | 5 |
| 64 KB, SHA-256 (MGF1) round functions | ≈ 17,800 (two-pipe) | ≈ 2,000× | ≈ 78× | 1 |
| §2c ARX butterfly with this chain (heuristic, scaled) | ≈ 525 ARX/B | ≈ 50–95× | ≈ 5–7× | 4; 8 on one SM |
| 15:50Z sponge (broken) | 13,200 | 2,100× | 85× | — |
| Budget | | 2× | 2× | |

- **Throughput:** 0.7 GB/s, i.e. about 1.5 s per GB of weights per forward pass.
- **Latency floor per segment:** about 28 sequential wide calls, about 0.3–0.5 s on a GPU, with all segments running in parallel. Enough for end-to-end tests on a small model; measure it.
- **Reference code.** `hashlib.shake_256` and `hashlib.sha256` are in the stdlib, which fits `protocols/`'s stdlib-only rule. Pin known-answer vectors for F, Π_2, P_T, H and one whole segment.

## Bottom line

- **Standard:** SHAKE256; Merkle–Damgård over a truncated permutation (an overwrite-mode sponge); SHA-256 Merkle commitments; Feistel indifferentiability at 8, 10 and 14 rounds, including the keyed form the tweak needs.
- **Heuristic but defensible:** Keccak-f as an ideal permutation, and running the two-permutation proofs with Feistel-SHAKE in place of Π_2 and P_T.
- **Real risks:**
  1. **The proof must be done in the two-permutation model** with this chain. The freshness argument of §1 and the pilot's `SpongeExPostFacto` are the work; the column game must allow held chaining values, which give one key and cost 1 + 512/m labels.
  2. **Locality** fits the margin by about 1 point.
  3. **Cost** is about 150× at prefill, which is workstream 2's problem.
  4. **Timing** is now the smallest risk: a level takes at least 4× Δ at a floor 5× below the measurement. It still rests on Daniel's no-ASIC scoping.

*Footnote (ASIC, out of scope).* An unrolled Keccak-f at 2–5 ns gives Π_2 = 19–48 µs, a level of at least 48 µs, and d ≤ 7.
