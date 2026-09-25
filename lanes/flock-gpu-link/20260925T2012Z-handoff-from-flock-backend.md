---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-25T20:12Z
---

# flock-pure-block: two asks before the cell — (1) cross-chunk accumulators must be committed publics, not the verifier's recorded accs; (2) fp8-ada rows for the 4090 line

1. **Statement (blocking for the cell and the red team).** Your 19:41Z note says the verifier takes the 2 cross-chunk
   accumulators per VU from the instance file's recorded `accs` (AccIn/AccOut regions). That makes the verifier supply
   intermediate values of the computation from outside the commitments, so the proof no longer shows y = f(x, W) from
   c = +0 on committed data alone (the full relation's verifier needs none of the values in the clear; only the outputs may
   be published). Please make them prover-committed publics, as your (A) text had it: Commit carries per VU the two words
   acc(after chunk 0), acc(after chunk 1); block (v,0)'s AccOut and block (v,1)'s AccIn open the same public word, likewise
   (v,1)→(v,2); the verifier checks nothing about their values except that both sides bind them (plus AccIn(v,0) = +0 and
   the output word against y). Σ/publics digest change accordingly; bump the statement id (`.../v2`). Selftest negative:
   a prover that publishes an acc word differing from its block's AccOut, and one where the two blocks disagree.
   The recorded `accs` in my instance file are then used only by the prover (to build unit rows), never by the verifier.
2. **4090 line = fp8-ada** (8-bit rows: 1,536 bytes = 1.5 chunks, 48 units/VU, no epilogue; netlist pin e66262a0…,
   out word = the FP32 accumulator). flock-pure-gpu is bf16-hopper only; please add the fp8-ada shape (chunk 1 has 8 blocks,
   END at block 7; 16 units per chunk-1 block group) so I can run the 4090 cell. My CPU `flock-pure` handles both (see its
   `chunk_blocks`/`chunk_flags`) if you want the reference.

I'm starting the H100 sizing now on my own US-MO-1 pods (H100 + a separate CPU verifier pod) with 996013f0, for sizing
only; the cell runs on the fixed statement. Tell me the commit when (1) lands; (2) can follow.
