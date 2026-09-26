---
lane: salted-leaves
kind: report
created: 2026-09-26T20:47Z
status: final
---

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

## FINAL

~~~text
tip: cursor/hm96-sha256-leaves-18a8 @ f1df809f (base main@2431e3c1)        merge-with: none
known-failures: vLLM integration, 10 pre-existing on 2431e3c1 + 2 order-dependent + 20 torch-less errors (list above) | core none
pod: none (CPU only); $0
artifacts: art:b3a08e21b4388350bada8c417d79bc419a9b857dbab14a6c455e27aee279e8f7 art:1e2b59f46b14402bae65aef4c9f10b230569ad1d37042a1467dfee00deac7f54
~~~

- **Recommendation:** hm96-sha256/v1 for every serving row leaf and for Flock's internal leaves (Daniel's decision), with the
  pinned key as the circuit constant. The 2% test is moot: hiding costs +128 bytes stored per row (3.1% at 4 KB rows, 50% at
  256-byte chunks), 5 native SHA-256 compressions and 3 in-circuit compressions per row. Choosing SHA-256 is what costs the
  circuit 2.1–2.4× today's keyed-BLAKE3 row ANDs.
- **Handoffs sent:**
  - `lanes/flock-netlist/20260926T2034Z-handoff-from-salted-leaves.md`;
  - `lanes/coordinator/20260926T2050Z-handoff-from-salted-leaves.md` (merge-ready).
- **Handoffs received:** none.
