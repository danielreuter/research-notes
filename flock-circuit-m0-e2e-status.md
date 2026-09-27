---
cursor:
  subagentId: "bc-84a84d8d-4e74-552a-b161-53abae2f342b"
---

# M0 `verity/flock-circuit` status for one-stage e2e (PR #83 tip)

Ref: `origin/cursor/flock-netlist-m0-4d6a` @ `eb90718f`. Read-only. Lane notes under `lanes/flock-netlist/`; format handoff `lanes/flock-verifier/20260927T0445Z-handoff-from-flock-netlist-format.md`. **PR #83 body is stale** vs tip (serving row leaf, SHA-512 digests, live `unit_draw` already landed).

## 1. STATEMENT

**Ids.** `verity/flock-circuit` (`circuit.rs` L42–47): formats `flock-circuit` / `flock-circuit-inputs`; scheme `frame-v3-sha512/hm96-sha512`; row `hm96-sha512/row/v1`.

**Pinned circuit.** `META` + `CIRCUIT` sections of `flock-ir-unit/v2`. Pin = **SHA-512(file)** → header `circuit_sha512` (`circuit.py` `digest` L315–318). No field named `pub.sha` on this branch; live keys are `circuit_sha512` / `public_sha512` (Lean archive CLI uses SHA-512 digests as object keys).

**META** (`compose` L269–276): ports, ranges, row constants, wires, leaves, `dummy` (`bc`+`outputs`), `leaf_scheme` (`hm96-sha512/v1`), lookups, **`program_digests`**, **`partition`** `{rule: flock-circuit/unit-cover/v0, digest: SHA-512(rule‖0‖canon(cover))}`.

**Public.** Frame-v3-sha512 roots; per-row **`b‖c`** (128 B); declared outputs; pinned layout. Regions `Digest(p)` / `Out` (`circuit.rs` L886–894). Verifier file: `rows: false` (no row/salt bytes).

**Instance header** (`write` L348–351): set/subcircuit/range/`instances`/`circuit_sha512`/`units`{indices,blocks}/`frame_v3`{roots,schemas,…}. Staged files refuse baked-in `unit_draw` (L698–700).

| Binding | Today? | Where |
|---|---|---|
| program digests | yes | META `program_digests` |
| partition digest | yes (provisional) | META `partition` |
| unit indices | yes | header `units` |
| `unit_draw` | yes, **live** | `Instances::drawn` L713+; `lib.rs` `unit_draw` L110+; after Register→Draw, before Hello |

**Σ.** `public_sha512` = SHA-512(sorted header ‖ pubs); statement digest SHA-512; Σ = SHA-512(`verity/flock-circuit/sigma` ‖ …) (`flock-circuit.rs` L86–93). Hello: `"digests":"sha512"`. Caveat: `identity().hashes` still *labels* statement/Σ as `"sha256"` (L78–80) while code is SHA-512.

## 2. INPUT

Registry **input set** → `lowering_for_set` → C-Flock template → `compose`/`stage` → `circuit.txt` + `inst-N.bin`/`pub-N.bin`. Slot circuits via `IL.netlist` (`_expanded` L284–287). **Not** `boolean_export` (visualizer only on main). **Not** a raw `Program` API.

**Measured cells:** `rope-head` d64 (8192 heads), `silu-mul` i8192 (128 rows), `rmsnorm-fused-cuda` / `rmsnorm-triton` n2048 (256). Relation `circuit:<template>`. Attention/Gemm/sampling modules exist; tensor-core output tails `NotImplementedError` in `compose` (L220–222). **No** path from one live vLLM served-row proof unit into this prover without an input-set + C-Flock lowering.

## 3. SESSION

**Binary** `flock-circuit`: `serve` | `prove` | `selftest` | `replay-coins`. Verifier = same binary `serve` on **`pub-N.bin`**. Modes: in-process selftest; loopback (`60-circuit.sh` MODE=bench); separate verifier pod (`61-circuit-cell.sh` + `circuit_bench`). Main’s `flock-live` is a different (BLAKE3-union) statement.

**Coins.** `coin_seed.rs`: OS seed+nonce; Hello → `SHA-512(tag‖nonce‖seed)` (`coin-commit/sha512`); derive domain `verity/flock-circuit/coins/v1`; open in verdict.

**Draw.** `serve --draw subset:K|bernoulli:NUM/DEN` → Register draws from OS (`unit_draw::draw`), rebuilds statement, Draw response; record keeps `unit_draw` (U1–U3).

**Records → Lean.** `--record-dir` → `selftest_records.py` → `archive-put` + `agree.py --lean flock-verify --upstream flock-circuit …`; also Rust `from_record`.

**Tables.** One `TableSpec "circuit"` per session. Multi-table = M1/M2 backlog.

## 4. GPU / CPU

CPU prover/selftest exists. **RoPE CPU wall time: not found** (pass counts only). GPU RoPE d64 L40S loopback (pre–row-leaf cells): **0.295 s** e2e / 1.57 G ANDs. Pods: L40S secure **~$1.09/h**, verifier RTX 4090 **~$0.74/h** (coord 00:50Z). `60-circuit.sh`: build+patch+stage+selftest/bench. `61-circuit-cell.sh`: cell sweep prover GPU / verifier CPU serve :7501.

## 5. SERVING ROW LEAF

**On tip** (`9e455f51`…`eb90718f`). Private rows+salts → in-circuit `sha512x3` (`x=SHA-512(prefix‖row)`) + `hm96` (`b‖c`); public opens `b‖c`; `check_public` rebuilds frame-v3-sha512 roots from `tree_leaf(key,b‖c)` (`circuit.rs` L1–23, L834–872). GPU device witness for row slots still incomplete (host upload path remains).

## 6. Next steps (lane order)

1. Device witness for row/`hm96` slots.  
2. L40S selftest + re-register four cells on new statement.  
3. Attention in circuit.  
4. Multi-table private glue (private-recursion will mirror format).  

Open: format published to flock-verifier (04:45Z); C1 done at `e2190ca3`; tip push may still need store bundle.

## GAPS for one-stage e2e

- No product path **serve commits → register population → verifier draw → prove units → Lean → integrity profile** (only input-set staging + optional `--draw`).
- Integrity-profile emission after Lean verify: **not found**.
- Partition digest provisional (`unit-cover/v0`), not `verity/partition/v1`; serving-root binding waits re-baseline.
- Lean #113 `unit_draw` live side is on tip; agreement vectors may lag until re-recorded.
- One table/template per session; attention + multi-table glue not in statement.
- GPU row-slot device witness / new-statement cells incomplete.
- `identity.hashes` labels lag SHA-512 digests.
- RoPE CPU prove duration: **not found**.
- `boolean_export` ≠ prover input.
