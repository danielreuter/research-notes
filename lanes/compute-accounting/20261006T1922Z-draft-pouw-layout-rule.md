---
id: 20261006T1922Z-draft-pouw-layout-rule
campaign: pouw
lane: compute-accounting
kind: draft
status: draft
repo: verity
origin: compute-accounting
---

# PoUW's side of the layout rule: a served window's drawn units as the recursion's instances

For proofs' scope of the layout rule (thread 1791300143.885349, reply 1791314469.036539). It is read at ci's tip 67
(`b0d0b1600`), which carries #1282, #1314 and #1322. Every name here is PoUW's code at that tip:
`verity/protocols/accounting/work/pouw/{window,circuit/pc8,circuit/leaves}.py` and
`benchmarks/pouw/served_zk/{served_commit,stage_tile}.py`.

## The unit

- **Definition:** `Pc8TileHidden{K, TM=1, TN=1, DEV=sm120}` (`circuit/pc8.py`, `Pc8TileHiddenDef`). It is `Pc8Tile` with
  its checked words hidden: it computes C̃_ij (the device's chain over A′_i·B̃_j) and U_ij (four BF16 k16 steps over
  P_A,i·P_B,j), and it returns only their tile digest (`leaves.PearlTileDigest`, `pearl_c.leaf` of C̃ and U).
- **Served shape:** K = 4096 for `o_proj`-shaped calls (k = n = K). Other k need `Shape.row_k`'s cut, which today's
  served window doesn't use.
- **One template per window:** every unit, filler included, is one instance of that one template at one K. That makes
  the population `population_program(Pc8TileHidden{K,1,1,sm120}, N)` under `Q_template_instance`.

## Its registered inputs

Each unit reads two committed rows and nothing else. They are the fp8-p rows of `leaves.words_fp8_p`:

| port | row | role | row schema | committed in |
|---|---|---|---|---|
| A side | A′_i ‖ P_A,i (the formed activation row and its clean-up half) | X | `hm96-sha512/row-seg/v1` | the entry's A-side root |
| B side | B̃_j ‖ P_B,j (the formed weight row and its clean-up half) | W | `hm96-sha512/row/v2` | the entry's B-side root |

- **Leaf:** each row's b ‖ c is hm96-sha512 over its SHA-512 row digest, under a fresh 192-byte salt.
- **Trees:** each side of each entry is one frame-v3-sha512 tree, under one-stage's served domain
  (`verity/one-stage/served-domain/v1`, bound by `identity_digest_sha512`). Its port is `<entry>/<side>`.
- **Window root:** each entry is one `hm96-sha512/row/v2` row of its SHA-512 in the window root (port `entries`), padded
  with empty entries to the public bound P.
- **Today's check** (`served_commit.check`) reads instance 0's b ‖ c from the proof's `pub.bin`. They must be the unit's
  A and B rows, each by its frame-v3 path to its entry's side root, and the entry by its path to the window root. The
  opening hands the verifier the drawn units' entries, which is a development shortcut.
- **What the rule must do instead:** the recursion's inner statement reads those two rows as registered inputs of
  instance t, at the positions `tile_at(entries, t)` names. `class_statement`'s synthetic inputs go. The verifier then
  reads only the window root, the draw and the outer proof.
- **Not read by the tiles today:** W's own root (`root_W`, each BF16 weight row a `hm96-sha512/row/v2` row). The tiles
  read each call's formed B̃ rows, until registered rows (P7) read B from W. That's a known leak in #1314's PR, separate
  from this rule.

## The N padded tiles

- **Real tiles:** each call's kept rows' products. N_real is their count (`window.window_problem`'s calls).
- **Padding:** the window registers grid level ℓ = `window.bucket(N_real)`, with GRID_BITS = 3 (integers with at most four
  significant bits). It is credited g_ℓ ≤ N_real tiles and pads to N = g_(ℓ+1), the least grid point at or above
  N_real + 1. That's the same grid as circuits' n_b (G6), so there is one bucket.
- **Filler:** every index in [N_real, N) is a filler tile, the same template on zero rows on both sides, committed like
  any row (kind `filler`). Lean `verify --zk` accepts its proof, and its proof has the same shape as a real tile's
  (r20261006-070934-e5f4: shape-filler SAME).
- **Index layout:** `window.window_problem` holds it. The entries are the calls, then one filler, then empty ones
  (`KINDS = call, filler, none`), and their ranges tile [0, N) in order. Unit t is `window.tile_at(entries, t)` =
  (entry e, A row i, B row j), so u = t − lo_e, i = a.keep[u // |b.keep|] and j = b.keep[u mod |b.keep|].
- **Draw:** P1's `Stream.select` opens the epoch's draw coin after the registration, and Lean
  `flock-verify draw --population N --k K′ --stream` samples K′ indices of [0, N). In the demo (ε = 1/2, δ = 1/10, 8192 real
  tiles), N = 9216 and K′ = 4.

## What PoUW needs from the rule

1. **Instance t of the inner statement is drawn unit t.** Its two registered inputs are opened at the positions that
   `tile_at` gives under the registered window root, so the outer proof shows that each drawn instance's rows are in
   the root.
2. **The window statement (L4) proved, not just checked in Python.** That covers the entry layout, the ranges tiling
   [0, N), and the level being `bucket` of the calls' tiles. Today `window_problem` runs only in the verifier's Python
   (a known leak).
3. **The only public items are `window.PUBLIC`:** the verdict, work (the level), check, sampling, the drawn indices and
   root_W. The entries, rows, salts and P's layout stay hidden (P1 ask 6).
4. **One recursive session per window,** with K′ inner instances of one template at one K, so the session has the fixed
   shape and a window's proof size doesn't depend on which tiles were drawn.

The open question for proofs: does the rule put the `tile_at` index arithmetic inside the outer statement (positions
read in gates, the joint note's step 8), or does the committer hand each instance its entry, with the outer proof only
checking the path? PoUW can work with either, but only the first removes the opening shortcut.
