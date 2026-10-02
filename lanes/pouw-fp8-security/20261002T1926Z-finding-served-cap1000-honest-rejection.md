---
id: 20261002T1926Z-finding-served-cap1000-honest-rejection
campaign: pouw
lane: pouw-fp8-security
kind: finding
status: closed
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); compute accounting's order of 9:46 AM PDT, 2 Oct (task 2)
---

# Pearl-C FP8 v1 at ρ = 1/1,000: no honest served tile goes over the cap

From FP8 security, 12:26 PM PDT, 2 Oct. The table is `art:dc6ba8a608a3fa215bbc5c0049fbb16dffe83b0b073d5425a1baf8929668d710`
(`table.md`, `table.json`, its builder, the replay's summary and every tile's record).

- **What was served.** Every Pearl-C FP8 run we have served is Llama-3.1-8B-Instruct in vLLM. That is 31 e2e windows
  (19 at `pearl-c-sm120-v1-h1`, 12 at `-h2`), every one on the same prompts, plus one WikiText-2 perplexity run. The
  shapes are prefill at m = 8,192, and decode at m = 32 with a prompt pass at m = 2,048. In each, k is 4,096 or 14,336.
- **The replay.** No served record holds a tile's debit; `verify.json` keeps only verdicts, at 1/400. So
  `r20261002-173355-4eef` replayed a seeded sample of tiles on CPU, from served window 5's retained passes
  (`r20261001-200934-8dbd`). The sample covers 1,023 of 4,816,896 tiles, stratified by shape. Each tile went through
  `check_tile` and `check_opened` at `Device.cap` = 1/1,000; the tool is `served_debit.py` on
  `cursor/fp8-served-cap1000-rate-cb26` @ e19032bd8.
- **The result.** 0 of 1,023 tiles are over the cap, and none failed its openings. The 95% upper bounds are 0.88% of
  tiles and 0.83% of credited MACs. The worst share is 0.0051%, which is 0.051 of the cap, on a decode tile at
  m = 32, k = 4,096, n = 6,144. By pass:
  - prefill: 0 of 512 over, worst 0.048 of the cap;
  - decode's prompt pass: 0 of 255, worst 0.044;
  - decode steps: 0 of 256, worst 0.051.
- **The perplexity run** (`r20260930-161427-313f`) kept no transcript, so it can't be replayed. The nearest is the CPU
  capture of the same model on the same split (`r20261001-083013-ae06`): 0 of 224 over, worst 0.052 of the cap.
- **With the earlier captures,** 0 of 1,422 honest tiles go over 1/1,000. The worst is still Qwen2.5's 0.40 of the cap.
