---
id: 20261001T0952Z-handoff-from-circuits-build-speed-665-ready
campaign: circuits-build-speed
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-build-speed (bc-d2d56312-a75e-56c6-a829-45a5135a3752)
---

2:52 AM PDT: [#665](https://github.com/danielreuter/verity/pull/665) (`cursor/build-speed-boundary-3752` @ 96cdfdc25) is ready (`research queue ready 665`) and needs the vLLM grant. It changes `query/module_body.py` and `query/required.py`: the manifest's two boundary passes (module body and `Q_word`) are numpy passes over the columnar read columns, and `read_by` (which no manifest reads) comes from `verity.proofs.query.boundary` when first read.

- **B1 4096/512 manifest:** 2,154 s to 1,244 s, peak RSS 23.7 GB to 5.0 GB; `manifest.json` is byte-identical (r20261001-084645-f17d vs r20261001-084659-7bd0).
- **Reference row:** the manifest stage went from 291 s to 259 s, with digests and `manifest.json` byte-identical (r20261001-084740-d533 vs r20261001-084746-c69e).
- **B1 256/32:** the manifest went from 94 s to 49 s, and the Build from 348 s to 286 s (r20261001-084751-86ba vs r20261001-084757-1c2c).
- **Tests:** both stored TP2 MoE rows pass alone, byte-exact.

It merges cleanly with `main`, #639 and #658, and touches no file they touch.
