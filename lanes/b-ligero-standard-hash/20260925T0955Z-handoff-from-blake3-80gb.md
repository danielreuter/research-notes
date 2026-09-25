---
lane: b-ligero-standard-hash
kind: handoff
from: blake3-80gb
---

# FYI: merging main 3301c435 into your tip conflicts in reverify.py (one hunk); main's file is the newer steps-pin version

lane/blake3-80gb 75cbbac1 = your 0ab2544f + main 3301c435 (+ my sweep_vu `--keep`). The only conflict was
`backends/direct/ligero/reverify.py` `commitment_problems`: your side carries ligero-steps-pin 06176b41's version, main carries
c8a16e2b's (hashed decided from the pinned system; stem-pairing check; v6 fails closed). I took main's file whole
(`git checkout --theirs`); nothing of yours differs there. Also: A100 bf16-ampere+blake3 4096 on your GPU-committer tree:
674.5 VU/s e2e, commit 0.014 s (art:855cc597). Note for sweeps: `research run --cwd source` runs in
/workspace/research/src/<sha>, whose fixtures lack the built vu-k1536 arrays -> pass `--root /workspace/src/fixtures/bench-instances/v1`.
No reply needed.
