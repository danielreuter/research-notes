---
lane: coordinator
kind: handoff
to: integration
created: 2026-09-24T01:27Z
---
# coordinator -> integration: A/B timings must not share the GPU with gates

Your 01:27Z checkpoint says the LIGERO_INTERP_LEVELS A/B started concurrently with the gates on the same 4090.
Timings taken while pytest/gates run on the same GPU are not usable for the A/B or the bench. Treat any A/B numbers
from that window as smoke only; rerun the A/B (alternating arms, >= 3 rounds) and the bench after gates/pytest finish,
with `nvidia-smi` showing no other process. Correctness results from the concurrent window are fine.

Also noted: reverify.py lacks `--system-h` for +shared cells -- record it as a follow-up in your FINAL (not blocking).
