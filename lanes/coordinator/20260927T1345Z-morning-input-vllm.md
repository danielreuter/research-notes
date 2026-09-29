---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: report · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T13:45Z · for: `docs/morning-report.md`

# vLLM, overnight (06:00–15:00Z): input for the morning report

## Headline (goal 2, `vllm-serving-commit`): serving now commits in M0's format, verified byte for byte on GPU

- **A2:** #101's served run commits all **183,680 RoPE heads** in M0's format (`frame-v3-sha512` rows, `hm96-sha512` leaves, SHA-512
  roots, registration record).
  - M0's own `write()` reproduces serving's public and prover files byte for byte.
  - The served rows equal the capture.
  - The e2e lane's A2 is `complete: true`, on the pre-canonical bundle and on the canonical partition (`17478e85…`).
- **A4, layer 0:**
  - P4: 12,341 non-GEMM units;
  - P6: the whole layer with shared GEMM rows, 6,771,765 units;
  - every member byte-identical to M0's writer.
- **Opt-in:** `vllm-v1` stays the record. Its run root `7adcef49` is unchanged in every served run, and #101's default manifest is
  byte-identical.
- **Overhead:** the serving hook takes 14.6–17.3 s of a roughly 190 s Commit stage. It hashes 70.5 MB, against about 908 MB for
  `vllm-v1`.
- **Merged:** PR #119, in train E1.
- **Spend:** about $5.5 of the $40.

## Goal 10 (`vllm-verify-optins`): all three opt-ins verified on real Builds

| opt-in | row | with it on | unset |
|---|---|---|---|
| FA3 `Check_inf` per iteration (#105) | #73, H100 | 0 violations and 0 recomputes over 1,164 specializations; −15.5 M gates; **H100 Match passes GM-01, 8/8** | equals the record row for row |
| Gemma weight + 1 once per norm (#109) | #57 | 57,855 recomputed Calls / 133 M gates → **0** | equals the record |
| FP8 scale products once (#106) | #74 | 146 G recomputed gates → **0**, at +1.15 G committed words; host products = old values at 2.72 G coordinates, 14/14 tokens | equals the record |

- **Follow-up:** #128 (`fp8.scale_products` through `F32Mul_v1`) is queued.
- **Spend:** $11.55 of the $20.

## Merged overnight (vLLM)

- **Train A:** #100 (the `check` + `research merge` gate), #98 (cross-Call check and member check), #99 (tap labels), #102 (the `MS`
  class for `max_scaled`), #103 (top-p `splits` total), #105 (FA3 `Check_inf`, opt-in).
- **Train B:** #106 (FP8 shared scale), #108 (the vLLM-shaped serving view of #101), #109 (Gemma `once`).
- **Train E1:** #119 (serving commits in M0's format), #137 (the MUFU ex2 shift clamp across C++, numpy, SP1, flock and CUDA).
- **Approved and queued:** #111 (the partition as a named query, P = Q(C)), then #120 (the program format spec,
  `verity/ir/PROTOCOL.md`) and #131 (`Q_template_instance`), plus #128.

## Spend

vLLM overnight: **$15.94 of $60** (guard tally: $739.09 at 06:10Z → $755.03 now). No pods are running, and the hard stop is $830.

## Decisions for Daniel

1. **The re-baseline epoch** (about $150–250, pending your budget since yesterday). It is where the opt-ins become the record:
   - FA3 v4 moves #73 and #74;
   - Gemma `once` moves #57;
   - FP8 shared scale moves #74: +17% committed interior words, and it needs the `scale_products` committer source;
   - the selection-order MoE router and the router, vocab, norm, guarded-max and `MS` taps;
   - the shared-greedy sampler moves #101;
   - serving commits in M0's format instead of `vllm-v1`.
2. **Old records can't be reproduced by digest.** The 09-22 records' Program digests can't be regenerated from any current tree: the
   Program id's `SRC` static embeds the capture wrapper's module path, which has moved (`609750e4` → `bfb0f1db`). The structure is
   identical, and verify-optins shows it row for row and on the manifest. Pin `SRC` independently of module paths, or regenerate the
   records at the re-baseline?
3. **The query of record.** It was also pending. The partition is now a named query (#111), so `Q_word` v1 would be the one to adopt.
4. **Small, no decision needed:**
   - a pre-existing flaky test, `test_transient_storage_is_released`: its allocation bound fails about half the time on main;
   - a top-p split reference totality fix, scheduled after this report (detail private).
