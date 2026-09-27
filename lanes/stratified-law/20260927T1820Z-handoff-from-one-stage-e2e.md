---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: stratified-law · kind: handoff · from: one-stage-e2e · created: 2026-09-27T18:20Z · status: final · repo: danielreuter/verity ·
origin: your 16:40Z handoff; PR #168 @ 60f7e28c (on #143, with #164/#161); Lean #167 @ ebc94ac5

# A4 P6 under `stratified:1024` is accepted and complete: every template drawn, at most 91,063 of 6,771,765 at 2⁻²⁰

- **The run:** `r20260927-170424-8360`, PRESERVED (record `art:39e89a007c9e`).
- **The re-audit:** a new registration `5c7ff8f0…` on P6's served files, unchanged. `previous` is P6's `0d1f8f84…`, and
  the window is P6's plus `reaudit: stratified-floor-1`.
  - The roots, scheme, leaf layer, anchors, partition, program and population all equal P6's (asserted).
  - R1–R6 pass with P6's record as the log, and P6's record still checks under its own law.
- **The draw:** `flock-verify draw --program --partition --stratified 1024` (#167). The fallback wasn't needed. Lean
  `draw-test` with the same flags accepts it, and `check_draw` holds it to `derive`'s law.

  | Template | n | k_s | drawn | per-template bound |
  |---|---|---|---|---|
  | RMSNorm Triton | 287 | 1 | **1** | 286 |
  | GEMM K = 2048 | 6,171,648 | 933 | 933 | 91,016 |
  | RoPE | 11,480 | 2 | 2 | 11,468 |
  | RMSNorm fused | 287 | 1 | **1** | 286 |
  | SiLU·mul | 287 | 1 | 1 | 286 |
  | GEMM K = 8192 | 587,776 | 89 | 89 | 84,773 |

- **The verdicts, 19 of 19:** 6 members × (M0's verifier, Lean U1–U3, Lean `verify` with units derived), plus
  `lean-draw/stratified-law`. The served shares equal the Lean draw.
- **The bound:** `wrong_units.bound` = **91,063**, as you predicted. The core profile's `law` is `stratified`, with the count
  drawn per stratum.
- **The negatives, 13 of 13 refused:**
  - **Your three:**
    - the registered law with one stratum's k changed, refused as `R1-law`;
    - a GEMM K = 2048 unit swapped for a second RMSNorm Triton unit, refused as `strata-count` by `check_draw`, and by Lean
      with "U2: stratum RMSNormTriton… holds 2 drawn units, not its k = 1";
    - a stratum's k written `true`, refused as `law` and `strata`, and by Lean with "U2: a stratum's k: not a natural
      number".
  - **One added:** the re-audit reusing P6's window, refused as `R6-window`.
  - **The nine earlier:** R2, R3, R4 with a null leaf layer, a draw outside the partition, a proved set short of the draw,
    C1, both C2 cases, and a session root not registered.
- **Pod:** an A100-SXM4 pod, because no CPU shape had stock. It ran 56 min wall against P6's 22.6, because 256 visible host
  cores oversubscribed a 42-vCPU quota. It cost about $1.9, and it's terminated.
