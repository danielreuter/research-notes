---
lane: coordinator
kind: brief
created: 2026-09-23T16:30Z
for: lanes leaf-iface, share-logup, ajtai-design, ajtai-leaf, blake3-leaf (+ red-team-leaf later)
---

> **Rules superseded (2026-09-24T01:00Z):** the standing lane rules (§0 and similar sections) now live in `~/.research/notes/kb/LANE-CONTRACT.md`, which wins where they differ. This brief's lane-specific content stands.

# Brief — the leaf campaign: three operand-commitment leaves (Poseidon2 · BLAKE3 · Ajtai) behind one interface, plus tile row sharing

## 0. Where you start (every lane)

* Repo `~/projects/verity` (one shared `.git`). Create a NEW worktree `~/projects/verity-main-wt/<lane>` on branch `lane/<lane>` from
  **`main` at e0cf2cd** (`git worktree add -b lane/<lane> ~/projects/verity-main-wt/<lane> main`). You never merge into main, never touch
  other worktrees, never delete other lanes' branches or pods. The coordinator merges; you deliver a branch that is `main` + your commits,
  `git status --short` empty, no conflict markers, no new `.md` in the repo (notes go to `~/.research/notes`, see below).
* Read, in this order: (1) `~/.research/notes/lanes/coordinator/20260923T1030Z-brief-wave2-device-lanes.md` §0–§2 (tooling rules: store,
  `research run`, pods, pushing, `machines.toml`, notes format, D7) — those rules apply verbatim; (2) `backends/direct/ligero/PROTOCOL.md`
  (whole thing; §§ on the linear test, lookups, coins/rounds, and the `included-hash` section near the end); (3)
  `~/.research/notes/lanes/hash-relation/20260923T0430Z-report-hash-relation.md` and its follow-ups in the same dir (how Poseidon2 is
  composed as a sponge along the chain, why it cost +65–72 % rows, their §6 remaining list incl. "row sharing via LogUp");
  (4) `~/.research/notes/lanes/coordinator/20260923T1215Z-report-morning-overnight2.md` §1–§3 (where the numbers stand, what is merged).
* Code you will touch or read: `backends/direct/ligero/hashchain.py` (Poseidon2 gadget + `compose(rel) -> HashedRelation`),
  `hashauth.py` (native row trees: Poseidon2 digests under SHA-256 indexed Merkle trees, `leaf/v2h`), `poseidon2.py` (numpy Poseidon2),
  `compile.py` (`LigeroCtx`, `Row`, `Linear(name, lin, c, pub)`, `Quadratic`, `System`, `ctx.lookup`), `relations.py` (registry; additive
  names only), `serialize.py` (`LIGSTM05` statement v5 = digests + leaf indices + roots + multiproofs, no operand words; `hash_name`),
  `protocol.py` (coin slots, rounds, tests), `relchain.py` (runner, `--auth included-hash`), `packages/verity/src/verity/commitments/rowleaf.py`
  (leaf framing; stdlib-only — NO numpy in `packages/verity`), Rust `backends/ligero-verify/src/{relation.rs,verify.rs,auth.rs}` + `tests/`.
* Tests: laptop = `uv run -q python -m pytest -q backends/direct/ligero --continue-on-collection-errors` (torch tests are skipped/errored on
  the laptop — expected) + `tests/test_repository.py` + `cargo test --release` in `backends/ligero-verify`; pod = the ligero tests with torch
  + `run.py gate-vu` (honest + negative family, 0 failures) + a bench with the Rust verifier accepting every sub-batch.
* GPU: exactly ONE pod per GPU lane (RTX 4090, the 24 GiB reference part: `uv run -q research pods create --name vy-<lane> --gpu "NVIDIA GeForce
  RTX 4090" --disk 60 --require-reference-part`), budget **$4 per GPU lane** ($0.74/h ≈ 5 h), terminate it yourself when done or at the
  deadline, annotate `machines.toml`. Set `LIGERO_GPU_STRICT=1` and `LIGERO_GRAPH_STRICT=1` on the pod. Ship `backends/shared` with your tree.
  Controls to compare against on the SAME pod (frozen `vu-k1536` set, 4096 VUs, l=16384): `fp8-ada` bare `--pipeline 4` ≈ 0.17 s local
  coins; `fp8-ada+hash` (Poseidon2, no sharing) ≈ 0.69–0.76 s. Local coins are fine today (label runs `mode=local-coins`, they are
  drill-downs); the coordinator runs the live-verified device wave tonight.
* Laptop disk is tight (3–9 GB free, not ours to fix): do NOT pull dump trees to the laptop; leave `proofs/` on the pod, push from the pod
  path with `research data put --preserve` as the Wave 2 brief describes, or push only `result.json`. Keep your worktree to one `.venv`.
* `backends/ligero-verify/DISCREPANCIES.md` is at its 48 KiB cap: do NOT add entries. Write D-style findings in your notes file under a
  `## Discrepancies` heading; the coordinator adds pointer stubs.
* Notes: `~/.research/notes/lanes/<lane>/20260923T1630Z-report-<lane>.md` (front matter `lane/kind/created/status`). Put a `CHECKPOINT <sha>`
  line at the top every ~45 min with a one-line state, and a `## FINAL` section at the end. The coordinator reads only that file, the
  branch, and your final message. **Deadline: FINAL by 23:00Z (16:00 PDT)**; checkpoint earlier if you finish. Everything you produce
  (result artifacts, gate logs) gets `research data put` + labels `--by <lane>`; no `verified=` labels (coordinator's job).
* Encouragement: the overnight lanes that mattered were the ones that measured, found the real bottleneck, and kept going past the first
  disappointing number. If the plan below is wrong, say so in the note with a number, then do the better thing.

## 1. Why this campaign exists

Table 2 column 2 ("+ in-proof hash") binds the private operands x, W to Merkle roots by hashing every operand row in-circuit with
Poseidon2-BabyBear. It works and is measured on four devices (+42 % on H100 BF16 … +175 % on the 4090). Two problems:

1. **Assumption.** Poseidon2 is an algebraic hash with young cryptanalysis; the rest of the system rests on BLAKE3 + a proven Ligero
   bound + a 186-bit challenge field. The user wants the same column under a standard hash (BLAKE3) and under a standard lattice
   assumption (Ajtai / Module-SIS), and wants to keep Poseidon2 as the third option — all three optimized under the SAME machinery.
2. **Cost.** Each VU hashes its own x row and W column (3 KB for BF16) although in a real GEMM tile a 64×64 block shares each x row across
   64 VUs and each W column across 64 VUs. Sharing divides in-circuit hashing by ~64 for ANY leaf, so the leaf choice becomes a
   security/comms decision, not a speed decision. That is where we want to be.

## 2. The interface (contract for everyone; `leaf-iface` implements it, others code against it from minute one)

New package `backends/direct/ligero/leaf/` with `base.py`, `registry.py`, one module per scheme (`poseidon2.py`, `blake3.py`, `ajtai.py`).

~~~python
class LeafScheme(Protocol):
    name: str            # "poseidon2" | "blake3" | "ajtai"  (relation suffix: "<rel>+<name>"; "+hash" stays an ALIAS of "+poseidon2")
    assumption: str      # one line for Table 1, e.g. "Poseidon2-BabyBear collision resistance (algebraic hash)"
    digest_elems: int    # BabyBear field elements per row digest (Poseidon2: 8; BLAKE3: 8 x 32-bit words as 16 x 16-bit limbs or 8 u32 -> decide; Ajtai: n)
    def native(self, rows: np.ndarray, *, word_bits: int, role: int) -> np.ndarray:
        """(R, digest_elems) int64 < p. Deterministic, unsalted in v1 (hiding only up to preimage search — say so in the note).
        Pure numpy/torch; this is what the committer runs and what the verifier checks against the SHA-256 tree leaves."""
    def leaf_bytes(self, digest_row) -> bytes:
        """Canonical framing of one digest for rowleaf.row_leaf (little-endian u32 per element unless the scheme needs otherwise)."""
    def gadget(self, ctx: LigeroCtx, words: Sequence[Expr], *, word_bits: int, role: int, carry_in: Sequence[Expr] | None,
               first: bool, last: bool) -> tuple[list[Expr], list[Expr]]:
        """In-circuit, per chain column: absorb this column's operand words into the running state.  Returns (digest_exprs_if_last,
        carry_out).  carry_in/carry_out are the values the chain carries to the next column (sponge state / chaining value / partial
        digest).  `last` column must return digest exprs that the compiler pins against the statement's public digest."""
    def witness(self) -> WitnessHook | None:
        """Optional device witness generator (see hashchain.Poseidon2Witness) for the gadget's hint rows."""
~~~

Rules: relation systems for `+poseidon2` must stay **byte-identical** to today's `+hash` (sys_id / table digests unchanged, Rust pins
unchanged) — the refactor is a move, not a change. Statement v5 already carries `hash_name`; extend it (or the system header) so the Rust
verifier knows the leaf scheme and checks `leaf_bytes` framing + the SHA-256 multiproofs generically. Rust pins become per
`(relation, leaf)`. Relation names are additive. Fingerprint: `authentication=included-hash`, `hash_name=<scheme>-<params>`, `sharing=none|tile64`.

## 3. Lanes

### 3.1 `leaf-iface` (4090, $4) — the interface + Poseidon2 as first plugin + Rust generalization. FIRST TO LAND.
D0 (target 18:00Z): `leaf/base.py`, `leaf/registry.py`, `leaf/poseidon2.py` (moved from `hashchain.py`/`poseidon2.py`), `hashchain.compose(rel,
leaf=...)`, `hashauth.build_row_tree(..., leaf=...)`, serialize/Rust carrying the scheme id; `fp8-ada+hash` == `fp8-ada+poseidon2` byte-identical
(assert in a test); `cargo test` green; gate `fp8-ada+poseidon2` 2048 VUs + negatives 0 failures on the pod; bench vs control unchanged.
Write `CHECKPOINT <sha> D0 LANDED` — the coordinator relays it to the other lanes (§9) so they rebase onto `lane/leaf-iface`.
D1: a `leaf/dummy.py` (identity-ish, insecure, test-only) to prove a second scheme plugs in without touching hashchain; conformance test
suite `leaf/conformance_test.py` any scheme must pass (native == gadget on random rows, framing round-trip, Rust pin/fixture generation
helper). D2: help `blake3-leaf`/`ajtai-leaf` integrate (read their notes dir; answer in yours under `## For other lanes`).

### 3.2 `share-logup` (4090, $5) — tile row sharing: hash each row ONCE per 64×64 tile. THE BIG NUMBER MOVER.
Today each VU's chain hashes its own x row and W column. Build the variant where a tile (64 x rows × 64 W columns = 4096 VUs = one batch) has
128 "row units" that hash the shared rows, and each VU proves its operand words EQUAL the shared row without re-hashing. Two candidate
mechanisms — measure the census of both, build the cheaper, write the soundness argument for it:
(a) **Fingerprint chain**: after the operand rows are committed, a verifier coin ρ (a new coin slot / round — protocol.py supports coin
    slots; keep 8c: challenges are functions of coins alone) ; each VU column computes f = Σ_j x_j ρ^j over the degree-6 extension as a
    LINEAR constraint (public coefficients ρ^j → `Linear` rows, near-free in the linear test) and the chain carries ONE field element
    (well, 6 limbs) across the 64 VUs sharing that row; the row unit computes the same f from the words it hashes. Collision prob
    ≤ 1536/|F| ≈ 2^-175 per row. Cost ≈ a handful of rows per column. (b) **LogUp** multiset argument between VU words and row-unit words
    (also needs a post-commitment challenge). Whichever: soundness must be added to `soundness()` in protocol.py and documented; Rust must
    verify it. Deliver `fp8-ada+poseidon2` with `sharing=tile64` gated (honest + negatives incl. "VU uses a word from a different row",
    "row unit hashes a different row", "ρ reused") and benched vs the no-sharing control; report rows/VU and t.total; then the same for
    `bf16-hopper+poseidon2` (gate only if time). Start on today's Poseidon2 path; rebase onto `lane/leaf-iface` when §9 says D0 landed.

### 3.3 `ajtai-design` (NO pod, $0) — parameters + security argument for an Ajtai (Module-SIS) leaf over BabyBear.
Deliver a design note (`~/.research/notes/lanes/ajtai-design/20260923T1630Z-report-ajtai-design.md`) by **19:00Z** with: (1) the hash
h = A·s mod p, p = BabyBear = 2^31 − 2^27 + 1, s = the row's committed bits (β = 1) — also evaluate nibbles (β = 15) and bytes; A public,
seeded (specify the seed → matrix derivation, e.g. SHAKE-256 of a domain tag); (2) parameter sets (n rows of A, m = row bits) for 128-bit
collision resistance, classical AND Core-SVP quantum, using the standard SIS→BKZ estimate (root-Hermite / Gaussian heuristic; cite the
method; cross-check against published Ajtai parameter sets at q ≈ 2^31–2^32, e.g. LaBRADOR/Greyhound/SWIFFT); state digest size in
elements and bytes for BF16 (1536×16 bits), FP8 (1536×8), FP4 (1536×4 + scales) rows; (3) the hiding variant h = A·s + B·r with short random
r (how many bits of r, what leaks without it: unsalted digests of low-entropy rows are preimage-searchable — same caveat as Poseidon2
today); (4) in-circuit design: the digest is linear in the committed bits, so the gadget is `Linear` constraints; the row is spread across
the chain's columns (48 columns × 32 words for fp8-ada) so the partial digest must be carried column to column (n carried elements per
column = +n rows/column; estimate n for each parameter set; note the alternative that carries only a random projection if a
post-commitment coin exists — coordinate with `share-logup`'s coin slot; and the alternative where only the 128 row units of a shared
tile carry digests at all); (5) statement format (digest elements as public per-column vectors, `Linear.pub`), verifier cost (rᵀA once per
batch), prover native cost (A·s per row on device); (6) the binding argument written for a red team: collision ⇒ short kernel vector,
concrete norm, why binary/short inputs are enforced by the existing range rows; (7) pitfalls list. Post a `CHECKPOINT` with a
provisional parameter set by **17:45Z** so `ajtai-leaf` can start coding against it.

### 3.4 `ajtai-leaf` (4090, $4) — implement `leaf/ajtai.py` against §2 with `ajtai-design`'s parameters.
Until the design note lands use a provisional (n = 256, β = 1, seeded A); make n a parameter. Native: A·s on device (torch int64 matmul mod
p, or split-limb int32). Gadget: the row's bits are already committed by the checker's range rows — find them (do NOT re-decompose);
per column emit `Linear` rows accumulating the partial digest into the carried state; last column pins the digest against the
statement. Rust: verify the linear constraint (it is a public linear relation over committed rows + public digest → falls out of the
linear test; check that the Rust verifier's linear test supports dense coefficient vectors efficiently — if not, implement rᵀA once per
batch). Deliver `fp8-ada+ajtai`: conformance tests, gate 2048 VUs + negatives (incl. "digest of a different row", "one bit flipped",
"non-binary s"), bench vs control; report rows/VU, t.total, digest bytes/row, statement bytes/sub-batch. Then `bf16-hopper+ajtai` if time.
Rebase onto `lane/leaf-iface` when §9 says D0 landed.

### 3.5 `blake3-leaf` (4090, $4) — implement `leaf/blake3.py`: BLAKE3 compression in-circuit, the conservative control.
Step 1 (first 60 min, no GPU needed): **census** — rows per 64-byte block for each design of the 32-bit ARX round in BabyBear
(31-bit field, so a u32 word = two 16-bit limbs): additions mod 2^32 with carry rows; XOR and rotations via bit rows vs. via lookup tables
(`ctx.lookup` is a one-hot selector over the table's distinct rows: 4-bit XOR table = 256 rows; 8-bit = 65536 — probably too big; measure
with the census, don't guess). Write the number: rows per block, blocks per row (BF16 row = 3 KB = 48 blocks; FP8 = 24), rows per VU
unshared and with tile64 sharing (÷64). Post it as a CHECKPOINT — the coordinator will decide with the user whether unshared is worth
running or only shared. Step 2: implement the compression gadget with the cheapest design + `native()` via the `blake3` package (must
equal real BLAKE3 of the row bytes with the standard framing — decide and document key/flags/chunk mode; a single-chunk-per-row design is
fine for ≤ 1 KiB, otherwise the chunk tree — state which and why). Step 3: `fp8-ada+blake3` conformance + gate (2048 VUs, negatives) + bench;
report rows/VU and t.total honestly even if ugly. Rebase onto `lane/leaf-iface` when §9 says D0 landed.

## 4. What "done" looks like (per GPU lane)
Branch = main + commits; tests green (laptop subset + pod full); gate 0 failures with the negative family; one bench artifact per relation
with the Rust verifier accepting all sub-batches (`ligero-verify batch`), pinned system; note with rows/VU, t.total vs the two controls,
digest bytes/row, statement bytes/sub-batch, assumption line for Table 1, and a `## Discrepancies` section; pod terminated; `machines.toml`.

## 5. Budget and pods
Four 4090 lanes × ≤ $4–5 + $0 design = ≤ $21 today. Ceiling $5/h total. Coordinator provisions the live verifier + device pods for the
evening wave (not you).

## 9. Coordinator appendix (I append here; re-read this section at every checkpoint)
* 16:30Z: launched leaf-iface, share-logup, ajtai-design, ajtai-leaf, blake3-leaf. No live verifier today; local coins.
* 17:00Z (COORDINATOR): budget ceiling is now $50/h and you may use an H100 80 GB (`--gpu "NVIDIA H100 80GB HBM3"`) if 24 GB or speed is
  the bottleneck (per-lane cap doubles to $8). Deadlines unchanged (FINAL 23:00Z) — the device wave for your columns runs 00:00Z–06:00Z,
  so a leaf that is gated on fp8-ada by 23:00Z gets measured on five devices tonight; one that is not, does not. New lanes that touch
  your area: `tier0-bytes` (serialize.py bit-packing + LIGSTM05 trimming — additive proof/statement magics, pins unchanged; if you change
  serialize.py, keep to the hashed-statement fields you own and note it), `fp4-decode` (5090 committed column; will consume the LeafScheme
  interface if it lands — leaf-iface: post the signature in your note by 18:00Z even before the code is done).
* 17:10Z (COORDINATOR): AJTAI-DESIGN FINAL is in `~/.research/notes/lanes/ajtai-design/20260923T1630Z-report-ajtai-design.md` (branch
  `lane/ajtai-design` @ 2a61a1f: `leaf/ajtai_params.py` + tests, no `leaf/__init__.py` so it merges after leaf-iface). ajtai-leaf: BUILD
  `ajtai-n64` (fp8/fp4, 48 steps <= 64, 256 B digest, 6n+1 = 385 rows/unit) and `ajtai-n128` (bf16-hopper, 96 steps, 512 B, 769 rows);
  Ring-SIS over F_p[X]/(X^n+1), beta = 1 (commit the 256 operand BITS per column), B from SHAKE-256("verity/ajtai-babybear/B/v1" || LE32(i))
  with rejection sampling; NOT n = 256 and NOT n = 96 (reducible). Their §8 messages to you: switch n, assert steps <= n, confirm acc_in rows
  are chain-linked (c_in = 0 at chain start), one `derive_B` for all call sites, expose `salt_bits` (v1 unsalted = binding-only, relation
  string must say `r0`). MEASURE the verifier chain-test growth (chain links 131/259 vs 19 today) — it is the one cost that can erase the
  win. red-team-leaf launches now against the note.
* 17:30Z (COORDINATOR — HARD RULE, user request): the LAPTOP IS NOT A COMPUTE OR STORAGE NODE. Disk is at 6.7 GB free and the user just
  lost work to it. Effective immediately: (a) NO `uv pip install torch`/cupy/triton in any laptop worktree — torch is on the pods only; I have
  UNINSTALLED torch from the leaf-iface, ligerito-proto and ligerito-sumcheck laptop venvs (each was +550 MB); if `import torch` fails on the
  laptop, that test belongs on the pod (`research run --on <pod>` or ssh); laptop tests are the numpy/pure-python subset only. (b) No dump
  trees, fixtures > 20 MB, or run-files pulled to the laptop (`research data fetch` only for manifests/results JSON). (c) No CPU-heavy
  long runs on the laptop (> ~1 min of 100 % CPU, e.g. parameter sweeps, 1e5 differentials, cargo builds of the big crate in parallel with
  others) — run them on your pod or on `vy-sp1`. (d) `cargo` builds: `--release` only when needed, `cargo clean` your target dir before FINAL.
  Check `df -h /` before anything that writes > 100 MB; if free < 4 GB, stop and note it.
* 18:00Z (COORDINATOR): RED-TEAM-LEAF FINAL (`~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md`): no BREAK.
  Ajtai: ship n = 64 (fp8/fp4) + n = 128 (bf16); best known attack k-tree 2^289 / 2^571, lattice floor 2^283 / 2^557; the design note's
  "M1 reproduces Buchmann-Lindner" argument is wrong (F1), so the coordinator writes the Table 1 line from the red-team numbers; the fully
  split X^n+1 gives no CRT gain. Handoffs in each lane's notes dir (`20260923T1800Z-handoff-coordinator-red-team-leaf.md`): ajtai-leaf F5/F6,
  share-logup F7 (soundness booking, ~14 b) + F8 (fingerprints publish ~248 bits of linear info per private row: v2 fold or label),
  leaf-iface F5 (per-leaf privacy note instead of the hard-coded Poseidon2 ZK_HASHED_NOTE), ligerito-zk F9/F10, blake3-leaf role-in-key.
* 18:10Z (COORDINATOR): LEAF-IFACE FINAL — `lane/leaf-iface` @ 720820d (D0 d35a52f + D1 conformance suite/dummy scheme/fixture helper +
  D2 registry families `register_family` / `suffix_of`, e.g. `fp8-ada+ajtai-n64`). Poseidon2 behind LeafScheme is byte-identical to `+hash`
  (same pins, identical transcripts, same prover time). Read its `## For other lanes` section NOW. **REBASE ONTO `lane/leaf-iface` 720820d,
  NOT onto main**: main moved to 22e10e0 (the other session merged vLLM v2; no file overlap with us, but it adds a torch-optional workspace
  member and they are testing in main's worktree). I integrate everything on `lane/integration` tonight. Per lane:
  - ajtai-leaf: your own `leaf/{base,registry}.py` + Rust `Leaf` will conflict — TAKE leaf-iface's and port Ajtai via `register_family`
    ("ajtai-n<N>"); Rust `leaf.rs` has only the Poseidon2 `SCHEMES` entry and an empty `PINS` table: add your entry + pin rows for n = 64
    AND n = 128 (+ the F6 B re-derivation). ALSO OWN red-team F5 for everyone: add a `privacy_note` attribute to the LeafScheme contract and
    make `relchain.ZK_HASHED_NOTE` / the fingerprint read it (Poseidon2 + BLAKE3: "deterministic, unsalted: hides only up to preimage search
    on a row"; Ajtai: "linear, unsalted: binding-only, leaks equality and linear relations between rows"). leaf-iface did not do it.
  - blake3-leaf: register via the registry, add your Rust `SCHEMES` entry + pin, set `privacy_note`, role in the key (red-team NIT).
  - share-logup: your one-system-two-roles `row_hash_system` needs an in-circuit role select; the contract's `gadget(role: int)` is
    compile-time — leaf-iface proposed an additive `role_row=` extension in its note (not implemented): implement it in your lane if you need it.
  - conformance suite runs on fp8-ada only; each leaf lane: also run it with `REL=bf16-hopper` on your pod before FINAL.
* 21:05Z (COORDINATOR): share-logup, ajtai-leaf, blake3-leaf went silent at ~19:00Z (pods idle). Replaced by `share-logup-2`, `ajtai-leaf-2`,
  `blake3-leaf-2` (brief `20260923T2100Z-brief-relaunch.md`; branches `lane/<name>-2` from the predecessors' tips; same pods). share-logup-2
  targets `+shared` at `--pipeline 4` <= 1.3x bare and all four relations; the leaf lanes measure `+shared` with their leaf if it lands by
  ~22:30Z. `red-team-leaf-2` ~22:30Z re-checks landed leaf code. FINALs 23:00Z (share-logup-2 23:30Z).
