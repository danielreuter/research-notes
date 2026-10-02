---
id: proofs/20261002T0627Z-finding-flock-protocol-md-trim-757
campaign: value-hiding
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/flock-hidden-outputs-95d4
---

# Text moved out of `backends/flock/verifier/PROTOCOL.md` (PR #757 merged with #730's train f38a)

#757 (hidden outputs) merged with `origin/cursor/train-prep-730-on-ff108ac24-f628` (`597e355d5`, #730 registered reads)
put the verifier's PROTOCOL.md at 132,656 bytes, over the 131,072-byte cap. The coordinator asked for at most about
130,000, leaving room for two §16.10 sentences (verifier-hm-pin, flock-public-ports). The merge is 129,840 bytes. These
lines left the spec: evidence counts, run ids, attributions and history, plus one stale duplicate and one superseded
target. The vectors, tests and checks they describe are unchanged.

Conflict hunks resolved to #757's side, which had already dropped these evidence pointers that #730's side kept:

~~~text
  and `sigma` read `sha512`. Sets 14 and 15 exercise it.
  - Set 13 (GEMM k1024) exercises them.
  claims must be an instance of it: then the statement's units are derived. `template_query_agree.py` checks the decoding
  against #131's `template_instance_vectors.json`.
  - **Tested** on #273's GEMM (`test_lean_typed_template.py`).
~~~

§18, the corpus counts (now a list of what `vectors.json` holds, by key):

~~~text
- **Honest sessions: 50 sets, 100 sessions,** each with `expect: accept`, taken from the verifier runs of cells that
  verify-flock-pure replayed and labelled `verified=accepted`, and red-team-flock(-2, -3) labelled `NON_ZK_PROOF`:
  - pure-block: `Chunk(3)` (H100, A100), `Fp8` (4090, H100), `ShaBf16`, `ShaFp8`, `Fp4`, `ShaFp4` (5090), `Chunk(n)` at
    real K (spine sets, L40S), 23 cells; point coordinates `m_pts` 26–28;
  - IR frame v2 and v3: elementwise (#101 and served), attention per-T (T = 4 … 257) and the three attention class cells,
    23 cells; `m_pts` 19–25;
  - IR sampling (2 cells, legacy L-SAMPLE) and vllm-block (1 cell, same verifier path, outside this spec's statements);
  - the PR #83 circuit statement: 2 loopback sessions of the SiLU 128-row run (`art:6250c04f`, `m_pts` 31, `os` coins).
  Each set names its record artifact, the verifier run and commit, the public input files, the recorded `Hello` and
  statement digest. Ten sets (the earliest pure-block cells) are pre-G2 records (§5.1).
- **Record-level negatives: 20 recipes.** Twelve ran on two cells in verify-flock-pure's replay run `r20260925-222222-a2cf`
  (`art:487b77de`), with outcomes: 9 rejected, 1 accepted as required, 2 informational. ... Eight new recipes cover
  S6 (D1), S11 (D2), S13, S15, a proof byte flip and a relabelled profile.
- **Forgeries: 12 red-team runs,** including R-BREAK (`art:8d04b53f`: ...). The runs stored their harnesses and verdict
  tables, not the forged records and proofs. Phase 2 materialises them with a `--dump` of each selftest case (the plan is in
  the manifest) before the Lean verifier's gate.
~~~

§17.1, D3 and D4's history (both closed upstream; the closing commits stay):

~~~text
- **D3:** ... Upstream's `from_record` ignored the field before PR #83 `b3baabd8`; Σ was bound there
  through `Hello` (S2) and `root_F` (S6). Found by fuzzing (seed 20260926).
- **D4:** ... Upstream ignored the retained bytes before its server retained them.
- **D5:** ... (set 16).
~~~

Evidence and attributions elsewhere:

~~~text
§7.3   `stratified_agree.py` ...: the derived law and population, against `draw.derive` and `partition.units`; the units
       drawn on given bytes, against the sampler written out in Python; every draw, from given bytes or the operating
       system's, accepted by `check_draw`; U2's verdicts on mutations of accepted draws, against `check_draw`'s; inclusion
       frequencies over operating-system draws, against `k_s / n_s`.
§7.3   ... records it; until then no recorded session carries one.
§15    2^-97.8 (red-team-flock's reproduction from the TOMLs; 2^-98.0 at m = 30) ... reps (red-team-flock re-audit).
§16.5  Upstream's composite verifier checks none of these, and every circuit of sets 0–15 meets them all.
§16.5  - Coins: `seed` mode at the PR's tip (...); the stored loopback sessions predate it and use `os` coins.
§16.7  `unit_cut_agree.py` checks the codes against the reference on random cuts (5000 agree, every code exercised)
§16.7  (`cut_check_agree.py`, `qword_agree.py`, `qword_program_agree.py`: every pinned vector, all of #101's Definitions,
       the LM-head `Gemm` in 100 s at 9 GB)
§16.10 (`HmRow.checkRegionWords`; the red team's C3, H_reg).
§16.10 Set 10's object, over RoPE's own program (a root batch), is refused with `--program`, as core's `evaluate` refuses it.
§5.1   (the ten earliest pure-block cells, §18)   ->   (the earliest pure-block cells, §18)
~~~

Stale text removed:

~~~text
§7.3 (the work law), a first draft of the bullet "Work and floors" replaced, ending mid-sentence:
- **Work.** Each template's PoUW work per unit comes from the verifier's own work table (`--work-table F`: a JSON
  object from template descriptor id to a natural number, in any fixed unit). Units that do no PoUW work, such as
  dequantization, the quantizer and attention, have work 0. A template the table does not name refuses the law
§16.5, the superseded SHA-256 target (§2: SHA-512 superseded it on Sep 26):
  The target leaf is `hm96-sha256/v1` (Halevi–Micali on SHA-256, PR #88). It publishes `b ‖ c` per row where today's
  leaf publishes the 32-byte digest, and it needs SHA-256 compression slots.
§16.9:
  The target statement (the circuit statement once its leaves move) pins SHA-256 on every commitment path: Halevi–Micali
  serving leaves on SHA-256 hashed in the circuit, SHA-256 Merkle trees, SHA-256 round digests (§2.5).
~~~

Added (§16.13): "**Registered reads** are §16.10's. A registered port is an input row: an output row is its instance's own."
