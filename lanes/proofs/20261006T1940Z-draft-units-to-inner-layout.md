---
id: proofs/20261006T1940Z-draft-units-to-inner-layout
campaign: proofs
lane: proofs
kind: draft
status: draft
repo: verity
origin: rec-units-layout
---

# From a served window's drawn tiles to the recursion's inner instances: the layout rule

This is proofs' scope of the layout rule, written for @proofs and for compute-accounting, whose side of it is
`note:20261006T1922Z-draft-pouw-layout-rule`. It answers that note's open question and its four needs. It was read at
`main` (`cb50af5e8`), at ci's tip 67 (`b0d0b1600`) for PoUW's window code (`pouw/window.py`,
`benchmarks/pouw/served_zk/served_commit.py`, `stage_tile.py`), and at the recursion stack's tip
(`cursor/registered-row-v2-fold-fa82`, `a9c858edb`) for `rec_*`, `InnerFold.lean` and the fixed outer shape (#1315). The
architecture it fills in is Daniel's `note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2` (PoUW:
L2, L3, L4 and local expansion) and the proof service's `note:proofs/20261006T0307Z-draft-proof-service-architecture`
(§4.1 step 8 and §6 step 8, the hidden layout). It is a scope only: no code was written.

## The gap

`verity_flock.class_statement` builds the recursion's inner statement as a synthetic layout: N instances of one Definition on
inputs drawn by `class_lanes` (`PU.synthetic_words`). Its docstring says so: it is not the scheme's layout rule. Nothing
binds a served window's drawn tiles, or the hm96-sha512 rows the window committed for them, to the inner proofs.

The served demo binds them another way, which is a development shortcut. `stage_tile.py` stages one drawn tile with
`class_statement.stage_unit` under the window's own salts, so the proof's `pub.bin` holds the same `b ‖ c` as the
window's leaves. Then `served_commit.check` hands the verifier the drawn tile's entry, its salt, the entry's path to the
window root and each row's path to its side root, and the verifier checks them in Python. That reveals the layout: the
entry (its sides' roots, row counts, kept rows, range and call record) and the rows' positions.

## The rule in brief

1. The inner statement of a window is `Cap.instances` instances of one read-bearing tile Definition. Instance s takes three
   public inputs: a tile index t_s, the window root and the window's tree domain. Everything else is private: the entry
   index and the entry row, the A and B rows, their window salts, and the paths.
2. The instance computes `tile_at` in gates. It opens entry e under the public window root, checks that the entry's range
   holds t_s, derives the rows i and j from t_s, opens both rows under the entry's side roots, and runs `Pc8TileHidden` on
   them. The verifier checks only that the public input words are its own: t_s is the s-th index of its own draw, and
   padding instances use t = N − 1, the window's last filler tile. It also checks that the window statement L4 is proved
   once per window over the same root.
3. This needs no new verifier form. The reads are gates inside a Definition, public input ports exist already (#846), and
   the window statement can use the existing registered reads. So it fits the 2026-10-04 ruling on the direct `--zk`
   path. On the recursive path it adds one input, the verifier's own public-input file, to a verifier side
   (`InnerFold.lean`) that already refuses plain leaves until their proof lands.

## 1. What an inner instance is

**An instance is one drawn tile.** It is not a proof unit of the window's own partition. The served population is
`population_program(Pc8TileHidden{K,1,1,sm120}, N)` under `Q_template_instance`, and P1's draw (`Stream.select`, then
`flock-verify draw --population N --k K′ --stream`) picks K′ distinct indices of [0, N). The inner statement does not
re-derive that draw. Its own Program is `population_program(TileRead, cap)`, where `TileRead` is the read-bearing tile
Definition of §2 and `cap` is the deployment's public `Cap.instances`. So its partition (`--program`, `--partition`,
`Q_template_instance` v0) names `cap` units, all instances of `TileRead`, and the statement proves all of them.

The draw reaches the statement through the public inputs. Instance s of session σ takes t = drawn[σ·cap + s] while that
index is in the draw, and t = N − 1 after it (§3). This keeps the statement's unit indices what the verifier's public-file
check expects (ascending, one per instance, in `HmRow.loadPublic`). Padding can repeat a tile index, but it can't repeat
a unit index. And the shape is a function of `cap` alone.

**Why not instance t = population unit t.** The Lean verifier has a drawn-population form (`HmRow.drawn`,
`Instances::drawn` upstream). There, the statement's instance i is a registered population's unit `units[i]`, selected
from a population public file published before the draw. For the served window, that file would hold every tile's
`b ‖ c` at public positions. With shared rows (`shared_rows`), it would also hold every tile's refs into its tables, which
is the layout. Committing N fresh-salted tiles before the draw also costs N tiles' commitments, not K′. The form is right
for the clear layout (the joint note's §6 step 0) and wrong for the hidden one.

## 2. How an instance's inputs bind to the window's committed rows

### What the window commits (`served_commit.commit_window`, at `b0d0b1600`)

- **Rows.** Each A row A′_i ‖ P_A,i is an `hm96-sha512/row-seg/v1` row of role X. Each B row B̃_j ‖ P_B,j is an
  `hm96-sha512/row/v2` row of role W. Each row is committed under a fresh 192-byte salt, and its leaf is
  `row_leaf(dom, i, tree_leaf(b ‖ c), schema)`.
- **Side trees.** Each side of each entry is one frame-v3-sha512 tree under `side_domain(params, ℓ, e, side, rows)`. The
  served domain binds the port `<e>/<side>` and the leaf count.
- **Window root.** Each entry (kind, lo, hi, each side's rows, keep list and root, and the call's record) is one
  `hm96-sha512/row/v2` row of the SHA-512 of its canonical JSON (`entry_bc`). The entries sit at port `entries` of the
  window root, padded with empty entries to the public bound P.
- **Window statement.** `window_problem` is L4 in Python, and nothing proves it yet.

### Three ways to bind, and the one to take

**(A) Registered reads at public positions** (`--registered`, `verity/registered-reads/v1`, `Flock.Registered`). This is
the existing form. The verifier derives each read's position from its own program, and it opens a registered root row by
row. For a drawn tile, the positions are `tile_at(entries, t)`, so the verifier would need the entries, which is today's
leak. The form also refuses the A rows: `Registered.Port.fits` requires a v2 row with no segments
(`q.v2 && q.segs.isNone && q.bits == words·wordBits`), and A is row-seg. Not this way.

**(C) The instance's own committed rows under the window's salts, opened by someone else.** `stage_tile` does this today.
The opening is checked either by the verifier, which leaks, or by V*, which needs the inner statement's row commitments
to reach V* as registered values. Under recursion, the inner statement has plain leaves (`flock-leaf/sha512-unsalted`).
Its row commitments are unsalted digests and functions of the hidden statement, which the firewall drops (live PROTOCOL
§10.3), so they can't be shown to anyone. Window salts on the direct path also leak equalities. Two drawn tiles that share
an A row (same call, same i) show the same `b ‖ c`, and over about 9,000 draws that pattern reveals each call's
|b.keep|, an architecture dimension. Not this way.

**(B) Hidden reads in gates inside each instance.** This is the rule, and it is the joint note's step 8 placed in the inner
instance. The instance is a Definition, `TileRead`, provisionally `Pc8TileServed{K, TM, TN, DEV, P, D}`, where P is the
entry bound and D is the side trees' fixed depth.

Its public inputs, as public input ports (`Flock.HmIn`, META `public_inputs`, `verity/flock-public-inputs/v1`), are:

- t, the tile index (40 bits, the range `served_commit.RANGE`);
- the window root (64 bytes);
- the window's domain id, and the side trees' domain ids if they differ (§2's requirements for PoUW).

The hm96 key is the pinned key, a circuit constant.

Its private inputs are:

- the entry index e and the entry row;
- the entry's window salt and its path to the window root;
- the rows i and j;
- the A row and the B row, their window salts, and their paths to the entry's side roots.

It checks, in gates:

1. **The entry is the window's entry e.** The entry row's `sha512/row/v2` digest gives x, then hm96 under its salt gives
   `b ‖ c`, and then the hm96 tree leaf, the frame-v3 row leaf at position e and the frame-v3 path under the window
   domain climb to the public window root.
2. **The entry's range holds t.** The entry's kind is not `none`, and lo ≤ t < hi.
3. **The rows are t's rows.** With u = t − lo, it checks u = i·n_b + j and j < n_b, where n_b is the count of B's tiled
   rows. With dense side trees, i and j are positions in those trees. With keep lists, they are positions in committed
   keep trees, read the same way.
4. **The rows are the entry's.** Each row's digest and hm96 commit under its window salt give a leaf, which climbs under
   the side domain to the side root the entry row holds. The A row uses the row-seg digest, the B row the v2 digest.
5. **The tile.** `Pc8TileHidden` runs on the two rows, and its tile digest is the instance's hidden output row.

**`tile_at` must be in gates.** compute-accounting asked whether the committer could hand each instance its entry, with
only the path checked. If the entry goes to the verifier, the layout leaks. If it goes to the instance privately and the
instance doesn't compute `tile_at`, the prover chooses (e, i, j) freely for every drawn t. It would prove the same good
tile for every draw, and the draw would bound nothing. Check 2 also relies on L4: without a proof that the ranges tile
[0, N) in order and don't overlap, a prover could commit two entries whose ranges both hold t.

**The verifier checks** only items it computes itself:

- the registration (`service.check_public`, `served_commit.public_problem`);
- its own draw;
- the window statement's proof (§4) over the registered window root;
- for each session, that the statement is `population_program(TileRead, cap)` (`--program`, `--partition`, and the
  identifier `verity/pouw/identifier/v1` with `--identifier`);
- that the public input words equal its own file F_σ (`--public-inputs F_σ`, `HmIn.checkOwn`).

F_σ is a function of the registration, the draw, σ and `cap` alone, and PoUW computes it (`window.public_inputs`, new).
The verifier never sees an entry, a position or a path.

**Fresh salts, no shared rows.** The instance's own committed rows (its inputs and its output row) take fresh salts, and
the statement is staged without `share_rows`. On the direct `--zk` path, their `b ‖ c` are in `pub.bin`, and fresh salts
keep them unlinkable. On the recursive path, sharing would change the inner table's shape (`dense_m`, `nbl`, which the
schedule reveals) as a function of which drawn tiles share rows. The window's salts appear only as private inputs.

### What PoUW's commitment has to change for gates

Requirement 1 goes into §6's questions; requirements 2 and 3 into §7's choices.

1. **An entry must be a fixed binary row, not a SHA-512 of canonical JSON.** Parsing JSON in gates is out. The entry
   becomes a fixed-width `sha512/row/v2` bit row: kind, lo, hi, each side's row count and root, and the record's SHA-512.
   Its keep lists either leave the entry or become committed keep trees.
2. **Side trees need public domains and a fixed depth.** Today `side_domain` binds e and the side's row count, both
   private, so the instance can't form the node hashes from public inputs. One domain per window and side, derived from
   the context and ℓ like `window_domain`, and side trees padded to 2^D leaves for a public D, make the read a function of
   (D, the public domain id).
3. **Kept rows: dense trees or keep trees.** If the side trees held only kept rows, in order, then i = u div n_b and
   j = u mod n_b would index them directly, with no keep read. The original row indices would stay in the call's record
   for P7, which reads B from W by its weight row. The alternative is one more hidden read per side, into a keep tree.

### What already exists for the gates, and what doesn't

`MerkleRead_v1{ARITY, D}` (`verity/primitives/commitments/gates/merkle.py`, #1050, with a `circuit_check.targets`
binding) is a hidden-position read. But its tree is plain SHA-512 over the children, with no tags. frame-v3-sha512 binds
every node to its domain, level and index, and every leaf to its schema and rank. So the window's trees need a frame-v3
variant: `FrameV3Read_v1{D}`, whose node hashes take the position's bits as private inputs. The hm96-sha512 leaf also
needs gates: c = SHA-512(salt_prefix ‖ y) is about two compressions, and b = x ⊕ M_key·y is XOR-only (hm96 PROTOCOL). The
subtree read `MerkleSubtreeRead_v1` (#1063, open) isn't needed for a 1×1 tile.

The cost per instance is two row digests (each row is roughly 4 KiB or more at K = 4096), three hm96
leaves, 2·D + ⌈log2 P⌉ frame-v3 nodes and a 40-bit multiply. The 2026-10-01 ruling accepts a hidden read's cost unless it
proves a bottleneck. circuit-check's report on `TileRead` gives the number, which also fixes `cap` (§3).

## 3. Padding and shape

**Window fillers need nothing new.** The tiles in [N_real, N) are the filler entry's zero-row tiles, committed like any
row, and `TileRead` reads them like any tile. N = `pad(N_real + 1)` > N_real, so every window has at least one filler,
and N − 1 is always a filler tile.

**Statement padding uses the public inputs.** `rec_shape` pads a statement to `Cap.instances` with fillers: zero rows and
the class's own output, staged by `class_statement --real`. Under `TileRead`, a zero-row instance would fail its reads, so
padding instances read a real tile instead. Instance s ≥ K′ − σ·cap of the last session takes t = N − 1. Its proof is the
filler tile's, which holds whenever the window is committed honestly. Its result is not credited, and nothing branches in
gates. Repeating a drawn index would work as well. N − 1 is preferable because the padding then has the same meaning as
the window's own filler and as `rec_shape`'s.

**The shape depends only on public items.** K′ = `window.k_prime(ε, δ, credited, n, w_max)` is at most N and a function
of the level ℓ. At ε = 1% and δ = 2^−128, it is 9,216 for the demo's level 87 (N = 9,216, so every tile is drawn) and
9,937 at level 143 (N = 1,179,648). At δ = 2^−64 it is 4,969. The demo's ε = 1/2 and δ = 1/10 give 4. With S(ℓ) =
⌈K′(ℓ) / cap⌉ sessions per window, each padded to `cap`:

- each outer proof has the cap's fixed shape (`rec_shape.check` refuses any other, as now);
- S is a function of the public ℓ;
- no outer proof depends on which tiles were drawn or how many tiles were real.

**A window with fewer real tiles than K′.** k_prime returns N, every tile including the fillers is drawn, and the last
session pads with N − 1. The credit is still g_ℓ ≤ N_real (`bucket`).

**One session per window** (compute-accounting's fourth need) holds only if K′ × |TileRead| fits one session. One session
has m = k_log + max(3, ⌈log2 blocks⌉) ≤ 35 with k_log ≤ 27 (`rec_vstage.shape`, `Hidden.klog_of`). At K′ ≈ 9,900, that is
2^35 / 9,937, about 3.5 M of the table per instance, and two 4 KiB row digests plus the paths may exceed it before the
tile's own gates count. PoUS's sampled setup is already 24 sessions for 8,828 blocks (Daniel's v2 note). The
recommendation is to plan S sessions from the start: `Stream.deliver` already takes several sessions' digests.

## 4. The window statement L4

L4 (`window_problem`) must be proved once per window: the entry layout, the ranges tiling [0, N) in order, and
`bucket(N_real)` = the registered level. Check 2 of §2 depends on it. It reads all P entries of the window root at public
positions 0..P−1, which is exactly the existing registered-read form (`--registered`, a v2 row per entry, so `Port.fits`
holds) over a root parameter. Its public inputs are ℓ, from which the verifier recomputes N and the credited count. It is
a small direct `--zk` statement with no recursion (P = 16 in the demo), and `service.Check.window` already names its
Program's SHA-512. The entry bound P, D and the entry row's layout are its parameters.

## 5. The PR sequence

Each step lists its owner, what it changes and what pins it. Steps 1–5 give a working direct path, with each window's
sessions verified by Lean `verify --zk`. Steps 6–8 put the same statements under the recursion.

1. **Frame-v3 hidden read in gates** (circuits or proofs).
   - Adds `FrameV3Read_v1{D}` and the hm96-sha512 leaf in gates, beside `gates/merkle.py`.
   - Pinned by tests against `frame_v3/vectors.json` and the hm96 `vectors_sha512.json`, a wrong-position control and a
     wrong-salt control.
   - Ships with circuit-check's report and a `circuit_check.targets` binding.
2. **The window's layout for gates** (compute-accounting).
   - In `served_commit` and `pouw/window.py`: the entry as a fixed bit row; side trees under per-window public domains,
     at a fixed depth D; dense kept rows, or keep trees.
   - `window.public_inputs(registration, drawn, σ, cap)` writes F_σ, with t = N − 1 padding.
   - Pinned by `window_vectors.json`: an entry row's bytes, a side leaf, the root of a toy window, and F_σ for a toy draw.
     The existing `window_problem` tests run on the new rows.
3. **`TileRead` = `Pc8TileServed{K,TM,TN,DEV,P,D}`** (compute-accounting, with proofs' review of the reads).
   - The §2 checks composed with `Pc8TileHidden`, with t, the window root and the domain ids as public input ports.
   - Pinned by the IR reference checked against `evaluate_bits` on a committed toy window, and by controls that must be
     unsatisfiable: t outside the entry's range, the wrong entry, a row from another entry, the wrong salt, and
     overlapping ranges (the case only L4 rules out).
   - Ships with circuit-check's report and a target binding.
4. **The L4 Program** (compute-accounting).
   - `window_problem` in gates over P registered entry rows, staged as a direct `--zk` statement with `--registered`.
   - Pinned by one control for each of `window_problem`'s refusals and by Lean `verify --zk` accepting the honest window.
5. **`class_statement.stage_window`** (proofs).
   - Stages session σ's `cap` instances from the committer's advice and prover rows (`advice.json`, `prover.npz`): fresh
     salts, no `share_rows`, `public_inputs` = F_σ. It replaces `class_lanes`' synthetic inputs for this class, and it is
     `stage_unit` generalized from one instance to `cap`.
   - Pinned by `backends/flock/tests/test_pouw_rows.py`-style pins of a two-instance toy window's statement digests, by
     Lean `flock-verify verify --zk --public-inputs F_σ --program --partition` accepting it, and by refusals of an F_σ
     naming another drawn index, a forged row and a wrong window root.
6. **The recursion's verifier side takes the verifier's own files** (proofs, rec lane).
   - `rec_vstage points` and `stage`, and `InnerFold.lean`, take `--public-inputs F_σ`, `--program` and `--partition` and
     pass them to `Stmt.setupTables` exactly as `FlockVerify.buildStmt` does. Today InnerFold passes only `partition`, so
     `HmIn.checkOwn` refuses any inner statement with public input ports, which is fail-closed and correct.
   - `rec_shape.Cap` is sized from `TileRead`'s META, and `class_statement --real`'s zero fillers are not used for this
     class.
   - Pinned by a CPU test that runs the recursion's verifier side on step 5's toy statement and refuses a one-word
     forgery of F_σ. Outer `verify` keeps refusing plain-leaves inner statements until step 8.
7. **The audit record** (proofs, sampled proofs).
   - The served challenger's `deliver` carries the S sessions' digests. `one_stage.audit.audit_record`, through
     `Stream.outcome(..., proved_units=drawn, instances=cap·S, ...)`, records F_σ's SHA-512 per session and the L4
     proof's session.
   - Pinned by `sampled_proofs` tests in which an outcome rejects a session whose F_σ is another draw's, or a window whose
     L4 is missing.
8. **Lean** (the soundness owner).
   - The plain-leaves headline, which the recursion already waits on (`Tags.plainLeaves`, `flock-leaf/sha512-unsalted`,
     #1284).
   - `InnerSound` (`cursor/rec-thm-95d4`, #1261) stated over the verifier side of step 6. Its hidden statement `x R ω`
     instantiates for PoUW as (the window registration, the draw) ↦ the `cap`-instance statement with F_σ, so VBridge's
     "each registered read carrying the registrant's value" becomes "each instance's public inputs are the verifier's
     own".
   - On main, `Discharge/Hidden/Spec.lean` covers `Stmt.setupHidden` when no public-input file is given (`checkOwn_none`).
     The `--zk` headline's tables include `HmIn`'s public-input filter (`Discharge/ZkHidden/View.lean`), but I did not
     confirm that a guarantee concludes that the instance read the verifier's words. The owner should confirm it before
     step 5's direct path is claimed sound.

## 6. Questions for compute-accounting

1. Can an entry become a fixed-width bit row (kind, lo, hi, n_a, n_b, root_a, root_b, the record's SHA-512) in place of
   the SHA-512 of its canonical JSON?
2. Can each side tree hold only its kept rows, in order, so that i = u div n_b and j = u mod n_b need no keep read? If
   not, can the keep lists become committed trees?
3. Can the side trees use one public domain per window and side (no e and no row count in the domain), padded to a public
   depth D? What is the largest side (rows per call) the declared range must allow?
4. What does a drawn tile's verdict assert beyond "its rows are the window's rows at `tile_at(t)`, and the template runs
   on them"? Today the tile digest is a fresh hidden output row that nothing compares. If the verdict must say the served
   result was right, the window has to commit each tile's served digest (or the served C rows), and `TileRead` compares
   it in gates. Which is it?
5. Padding: is t = N − 1 (the window's last filler tile) acceptable for the instances past K′? The alternative is
   repeating drawn indices.
6. One session per window can't hold K′ ≈ 9,900 at ε = 1% and δ = 2^−128 unless an instance stays under about 3.5 M of
   the table. Is S(ℓ) = ⌈K′ / cap⌉ fixed-shape sessions per window acceptable? It is public, as a function of ℓ.
7. Which ε, δ and declared level range [lo, hi] does production use? They fix the largest K′, and so `cap` and S.
8. Is L4 a separate direct `--zk` statement per window (recommended, §4), or must it share the recursive session?
   Sharing would make the inner statement two templates, not one.
9. P7, reading B from W: when it lands, does a B row's leaf carry its weight row index, so that `TileRead` reads W at it?
   That would be a third read per instance.

## 7. Risks and open choices

- **Session size** (risk).
  - K′ × |TileRead| may need many sessions per window, and each session costs one V* outer proof (437.8 s of outer Lean
    verify in #1284's measurement).
  - Recommendation: measure |TileRead| with circuit-check as step 3 lands, before sizing `cap`. Plan S sessions per
    window, not one.
- **Hashing twice** (cost).
  - On the direct path, C-Flock commits the instance's input rows itself, under fresh salts. That computes each row's
    digest x, and `TileRead` computes x again for the window leaf.
  - Recommendation: accept it at first (the 2026-10-01 ruling). Later, either let the instance's rows be plain witnesses
    with no C-Flock commitment, or expose C-Flock's in-circuit x to the Definition. Either is an upstream question for
    C-Flock, and neither changes the verifier.
- **frame-v3 in gates, or MerkleRead's plain tree.**
  - PoUW could commit its window under `MerkleRead_v1`'s untagged fixed-depth tree, with no new read Definition.
  - Recommendation: keep frame-v3-sha512 and add `FrameV3Read_v1`. The service's `SCHEME` is
    `frame-v3-sha512/hm96-sha512`, and L4's registered reads open the same window root natively. Two tree formats for
    one root would be worse.
- **Unchecked public-input coverage** (risk).
  - If no guarantee states that an accepted statement's instances read the verifier's public words, then accepting them
    is a form ahead of its proof, under the ruling. That would hold for PoUW's anchors today as well.
  - Recommendation: confirm it first (step 8's last item). If the proof is missing, it goes in before step 5 claims a
    sound direct path.
- **The ruling's fit.**
  - The rule fits. A new workload, such as another K or another tile template, is a new `TileRead` binding through
    circuit-check, with no verifier or proof change. The inputs and outputs keep the one canonical format: hm96 rows and
    public input ports.
  - The one thing the recursive path gains, the public-input file in `InnerFold`, is a form the direct verifier already
    has. It stays refused on the recursive path until step 8, as plain leaves are now.
- **Leaks this rule doesn't close.**
  - P7: the tiles read formed B̃ rows, not W's.
  - P, D and `cap` are public. Here they are deployment parameters, not per-window values.
  - S(ℓ) and K′(ℓ) reveal only ℓ, which is already public as `work`.
- **The draw-to-F_σ map is PoUW's code, not Lean's.**
  - The verifier of record computes the draw (`flock-verify draw`), but F_σ is written by `window.public_inputs`, as
    anchors are today.
  - Recommendation: pin it with vectors (step 2). If a later ruling wants the whole map inside the verifier, it can
    become a `derivation` the Lean verifier recomputes; `HmIn` ports already name a `seed` and a `derivation`.
