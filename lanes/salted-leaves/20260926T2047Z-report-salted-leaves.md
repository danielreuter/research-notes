---
lane: salted-leaves
kind: report
created: 2026-09-26T20:47Z
status: final
---

CHECKPOINT cd00f704 (22:34Z) [final] PR #88 C1/C2 fixed @ a53900df (merge first as hm96-sha256/v1); E4 PR #93 @ cd00f704: hm96-sha512/v1 + frame-v3-sha512 + vllm-v1-sha512 opt-in, costs art:b9bb217f (per row) art:a7a8ccce (trees); handoffs to coordinator and flock-netlist
CHECKPOINT cd00f704 (22:33Z) [final] PR #88 C1/C2 fixed @ a53900df (merge first as hm96-sha256/v1); E4 PR #93 @ cd00f704: hm96-sha512/v1 + frame-v3-sha512 + vllm-v1-sha512 opt-in, costs art:b9bb217f (per row) art:a7a8ccce (trees); handoffs to coordinator and flock-netlist
CHECKPOINT a53900df (21:56Z) [open] PR #88 C1/C2 fixed @ a53900df (merge-ready handoff sent); starting E4 follow-up: hm96-sha512/v1 + SHA-512 frame-v3/vllm-v1 tree framings (stacked PR)
CHECKPOINT a53900df (21:53Z) [open] reopened for red-team-hm96 conditions C1/C2/F4: NOT final; fixes pushed at a53900df
CHECKPOINT f1df809f (20:49Z) [final] hm96-sha256/v1 in core + opt-in vLLM host committer, PR #88 @ f1df809f (branch bound: cursor/hm96-sha256-leaves-18a8); per-row cost art:b3a08e21; handoffs to flock-netlist and coordinator
CHECKPOINT f1df809f (20:49Z) [final] hm96-sha256/v1 in core + opt-in vLLM host committer, PR #88 @ f1df809f; per-row cost art:b3a08e21 (hm96 ANDs 2.13-2.44x keyed-BLAKE3 row at 1.5-8 KB, +128 B/row); handoffs to flock-netlist and coordinator
CHECKPOINT f1df809f (20:47Z) [open] hm96-sha256/v1 in core + opt-in vLLM host committer on cursor/hm96-sha256-leaves-18a8 @ f1df809f (PR #88); per-row cost run r20260926-204634-0958 art:b3a08e21; handoff to flock-netlist written

# salted-leaves: `hm96-sha256/v1` hiding leaves

Branch `cursor/hm96-sha256-leaves-18a8` ([PR #88](https://github.com/danielreuter/verity/pull/88), draft; this agent's branch
naming rule, not `lane/salted-leaves`). Daniel's decisions: Halevi–Micali leaves unconditionally (no 2% threshold, no salted-BLAKE3
fallback), with SHA-256 as the collision-resistant hash.

**A correction to the brief.** The vLLM serving path commits vllm-v1's SHA-256 position leaves (`pos_leaf`), not
`blake3-keyed/row/v2`. That schema is frame-v3's research row leaf, the one Flock's circuit hashes today. Both are unsalted, so the
motivation holds.

## What landed

**Core: `verity.commitments.hm96`.** Spec `hm96/PROTOCOL.md`, a stdlib reference, `vectors.json`, and `test_hm96.py` (35 tests).
- The leaf wraps any SHA-256 leaf digest x:
  - `y`: 128 OS bytes;
  - `c = SHA-256(salt prefix ‖ y)`;
  - `b = x ⊕ M·y`, with `M[i][j] = key bit (i + j)`, 256 × 1024, and a 160-byte key;
  - `leaf = SHA-256(prefix ‖ SHA-256(key) ‖ b ‖ c)`.
- Hiding is statistical, by the generalized leftover hash lemma:
  - a uniform key gives N·2^-256;
  - the pinned key gives N·2^-192 for all but 2^-64 of keys;
  - so 2^-128 holds at N = 2^64.
- Binding rests on SHA-256 collision resistance only, for any key.
- `Hm96Sha256(VllmV1, key)` is the configured scheme.

**vLLM: `NativeHostCommitter(leaf_scheme="hm96-sha256/v1")`, off by default.**
- `commit.hiding` is a numpy batch path pinned to core's vectors.
- Salts are retained per step and counted in persistent bytes.
- Openings and range openings carry their salts.
- The scheme digest is bound into the step context.
- The default leaves and roots are unchanged; `test_native_host_security` passes.
- The GPU chunk tree and padding steps are refused under hm96.
- `open_levels` moved to `native_ranges` (P10 cap 2572 → 2563).
- There is no CLI flag yet: `pipeline/commit.py` is at its P10 cap, and the switch lands with the epoch.

**Bench:** `benchmarks/commitments/hiding_leaf_cost.py`, registered as the tool `hiding_leaf_cost`.

## Measured per row

Run `r20260926-204634-0958`: result `art:b3a08e21b4388350bada8c417d79bc419a9b857dbab14a6c455e27aee279e8f7`, run files
`art:1e2b59f46b14402bae65aef4c9f10b230569ad1d37042a1467dfee00deac7f54`, from clean commit f1df809f. Host times are one core of this
4-vCPU VM, with SHA-NI, the `blake3` 1.0.9 wheel and 8,192 rows × 7 reps. ANDs use the ripple-carry model: 22,696 per SHA-256
compression and 10,416 per BLAKE3 compression. hm96 is shown over the circuit-friendly `sha256/row/v1` inner digest.

| row B | stored | ANDs, keyed-BLAKE3 row (today) | ANDs, hm96 | ratio | µs/row: BLAKE3 row / pos-leaf / hm96 over pos-leaf |
|---:|---:|---:|---:|---:|---|
| 256 | +128 (50%) | 41,664 | 181,568 | 4.36× | 0.54 / 0.51 / 2.92 |
| 1,536 | +128 (8.3%) | 260,400 | 635,488 | 2.44× | 1.50 / 1.18 / 3.59 |
| 3,072 | +128 (4.2%) | 520,800 | 1,180,192 | 2.27× | 1.97 / 2.15 / 4.53 |
| 4,096 | +128 (3.1%) | 697,872 | 1,543,328 | 2.21× | 1.31 / 2.68 / 5.08 |
| 8,192 | +128 (1.6%) | 1,406,160 | 2,995,872 | 2.13× | 2.00 / 4.79 / 7.17 |

- **In the circuit,** hiding itself is 3 SHA-256 compressions (68,088 ANDs) plus 135,803 XORs per row. The rest of the gap to
  today's BLAKE3 leaf is SHA-256 hashing the row, since one compression costs 2.18× a BLAKE3 compression.
- **Serving, natively,** adds 5 SHA-256 compressions per row: +10% at 3 KB, +100% at 256-byte chunks. The host adds a flat
  ~2.4 µs per row on one core (Python and numpy; salts, the table product and two hashlib calls).
- **Salted keyed BLAKE3, the baseline:** +32 bytes stored per row, 1.01–1.25× the ANDs, and hiding only in the random-oracle model.

## Coordination

Handoff `lanes/flock-netlist/20260926T2034Z-handoff-from-salted-leaves.md`. It covers:
- the row format for their circuit;
- the same function for `flock-leaf/hm96-sha256`;
- that their reserved sizes match (128-byte salt, 160-byte key), with one key per tree enough;
- that ChaCha20-drawn salts make the hiding computational;
- an offer of a frame-v3 hm96 schema if M0 needs one.

## Open

- A GPU committer kernel for hm96 (commit-gpu): 5 SHA-256 compressions plus a 128-lookup table product per row.
- `--leaf-scheme` in `pipeline/commit.py` at the epoch; that file needs a split first, since it is at its P10 cap.
- Padding steps under hm96. Padding values are public by construction, so unsalted padding leaves would do; not implemented, and
  refused for now.
- B-Ligero's accounting (`hm_commitment_hiding`, k = 160, x of 6k + 4 bits) takes |x| = k, but SHA-256 digests have |x| = 256.
  hm96 §3's direct bound applies to the affine family. Frozen backend: not changed.

## Tests

- **Core:** 1,078 passed.
- **vLLM integration:** 12 failures and 20 errors, all pre-existing or environmental:
  - 10 failures also fail on base 2431e3c1;
  - 2 are order-dependent and pass alone (`test_lifted_tiny::test_specified_list_is_closed`,
    `test_twins::test_check_writes_the_evidence_schema`);
  - 18 collection errors and 2 `test_llm` errors come from torch, which this VM lacks.
- **Lints P1–P10 and the dead-code census:** pass.
- One failed attempt, `r20260926-204552-c862`, was an invocation error (a relative script path without `--cwd`), rerun as above.

## Red-team conditions (reopened 21:53Z)

red-team-hm96 granted PR #88 with conditions (`lanes/coordinator/20260926T2140Z-handoff-from-red-team-hm96.md`, `art:6f13f90a`).
Both conditions are fixed on the same branch at `a53900df`.

- **C1, finding 1 (b8132bdf): hm96 fails closed on the leaf path taken.**
  - The context digest binds hm96 only for a step whose leaves were salted, and every step root goes through it (host path,
    `commit_block_offline`, the native collector).
  - A committer whose step path is overridden, or that uses the GPU tree, is refused at construction; that covers
    `NativeCollectCommitter` with `native_worker` on or off.
  - `verify` and `verify_range` reject a step without one salt per leaf, and `finalize` refuses such a run.
  - There are 5 new negatives, all failing on f1df809f.
- **C2, findings 2–4 (a53900df):**
  - the pinned-key bound, with its condition, in hm96 §8, the docstrings and the README;
  - `verity.claims` entries `statistical-hiding` (guarantee) and `common-reference-string` (model);
  - the `/leaf=` suffix and its injectivity condition in vllm-v1 §4, with a test;
  - the hm96 leaf rule in vllm-v1 §5 and §9;
  - "statistical given uniform salts" wherever salts are discussed;
  - finding 6 as a spec rule: the key is never a witness.
- **Tests:**
  - core, protocols, repository, bench views and vLLM lints: 1,209 passed;
  - vLLM commit and acquire tests with CPU torch: all pass except `test_compiled_source::test_renumber_…`, which also fails on
    f1df809f and depends on the torch version.

## E4: SHA-512 data commitments (follow-up PR #93, stacked on #88)

Daniel decided on SHA-512 on every commitment path, and the root assigned me the frame roots too.
[PR #93](https://github.com/danielreuter/verity/pull/93) is branch `cursor/sha512-commitments-18a8` @ cd00f704, based on #88's
a53900df; retarget it to main after #88 merges. Everything is opt-in, and the SHA-256 defaults are byte-identical: every existing
vector passes.

- **`frame-v3-sha512` and `vllm-v1-sha512`.** Each is the framing through SHA-512.
  - Scheme-computed digests are 64 bytes; identity digests stay 32 bytes.
  - `sha512/row/v1` has a 128-byte constant prefix block.
  - Specs: frame-v3 §6 and vllm-v1 §10.
  - `vectors_sha512.json` sits beside each.
- **`hm96-sha512/v1`.** A 1,536-bit salt, a 512 × 1,536 Hankel matrix and a fixed, public 2,047-bit key.
  - The bound is the same as hm96-sha256's.
  - The setup claim is spec §2a, and `verity.claims` gains `hash-derived-key`.
- **Per-row cost** (run `r20260926-221723-71aa`, `art:b9bb217f74d4dbe95ca6d6594b1330c005063e0c45d8f2cfb0aecde0ae8673c6`), ANDs over the
  keyed-BLAKE3 row:

  | row bytes | ANDs, hm96-sha512 | ÷ keyed-BLAKE3 row | ÷ hm96-sha256 | stored |
  |---:|---:|---:|---:|---:|
  | 1,536 | 871,800 | 3.35× | 1.37× | +192 B |
  | 3,072 | 1,569,240 | 3.01× | 1.33× | +192 B |
  | 8,192 | 3,894,040 | 2.77× | 1.30× | +192 B |

  Hiding itself costs 116,240 ANDs plus 400,193 XORs per row. On the host, hm96-sha512 adds ~3.8 µs per row, against 2.4 µs for
  hm96-sha256.
- **Tree cost** (run `r20260926-221754-0cce`, `art:a7a8ccce9ed178c0636d9644296b152fc3144f97204198a1d9a215ccc5fc99f3`): the
  SHA-512 framings commit 1.31–1.39× slower through the Python references on this SHA-NI CPU. Per message the compressions are about
  equal.
- **Tests:** core, benchmarks, Ligero auth, vLLM production vectors, hiding and lints: 1,353 passed.
- **Not in #93:**
  - the integration's SHA-512 committers (Python and CUDA), listed in vllm-v1 §10, which land at the re-baseline;
  - SHA-512 identity digests;
  - capture-v1.

## FINAL

~~~text
tip: cursor/hm96-sha256-leaves-18a8 @ a53900df (base main@2431e3c1; red-team C1/C2 fixed); E4 follow-up cursor/sha512-commitments-18a8 @ cd00f704 (base a53900df)        merge-with: #88 first, then #93
known-failures: vLLM integration, 10 pre-existing on 2431e3c1 + 2 order-dependent + 20 torch-less errors (list above) | core none
pod: none (CPU only); $0
artifacts: art:b3a08e21b4388350bada8c417d79bc419a9b857dbab14a6c455e27aee279e8f7 art:1e2b59f46b14402bae65aef4c9f10b230569ad1d37042a1467dfee00deac7f54 art:b9bb217f74d4dbe95ca6d6594b1330c005063e0c45d8f2cfb0aecde0ae8673c6 art:8750691de6491b68d1c7f2e47011fc1ab6aee0c84c63053cf6638dc308c17622 art:a7a8ccce9ed178c0636d9644296b152fc3144f97204198a1d9a215ccc5fc99f3 art:c05bbf25a8af87949e10f4aa49eca92255111f9bbc7ca7a993e20a54b0819bae
~~~

- **Recommendation for the re-baseline:**
  - Use `hm96-sha512/v1` leaves over `sha512/row/v1` rows of 1.5 KB or more, inside `vllm-v1-sha512` trees, with the pinned key as
    the circuit constant.
  - The cost: +192 bytes stored per row (4.7% at 4 KB), 4 native SHA-512 compressions, and 2 in-circuit compressions (116,240 ANDs)
    per row.
  - Choosing SHA-512 is what costs the circuit 2.8–3.4× today's keyed-BLAKE3 row ANDs at 1.5–8 KB, and 1.30–1.37× hm96-sha256.
  - `hm96-sha256/v1` (PR #88) stays for SHA-256 roots.
- **Handoffs sent:**
  - `lanes/flock-netlist/20260926T2034Z-handoff-from-salted-leaves.md`;
  - `lanes/coordinator/20260926T2050Z-handoff-from-salted-leaves.md` (merge-ready #88 @ f1df809f, superseded by the next);
  - `lanes/coordinator/20260926T2158Z-handoff-from-salted-leaves.md` (C1/C2 fixed, #88 @ a53900df);
  - `lanes/coordinator/20260926T2225Z-handoff-from-salted-leaves.md` (E4, #93);
  - `lanes/flock-netlist/20260926T2225Z-handoff-from-salted-leaves.md` (SHA-512 sizes; the key is never a witness).
- **Handoffs received:** none in my inbox. red-team-hm96's findings reached me through the root:
  `lanes/coordinator/20260926T2140Z-handoff-from-red-team-hm96.md`.
