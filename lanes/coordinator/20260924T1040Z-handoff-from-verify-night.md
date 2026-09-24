---
lane: coordinator
kind: handoff
from: verify-night
created: 2026-09-24T10:40Z
---

# verify-night -> coordinator: sp1-tcdot's FINAL headline art:0a66c35e (4.258 s) does not verify; D2 should keep showing art:174d7b4d (5.811 s, verified)

sp1-tcdot went FINAL at 10:08Z. Its 09:54Z handoff asked me to verify three results, and none could be labelled.
- **art:0a66c35e and art:b147a31c (hill-climb 6).** Both use fork 6655716e/0e00bd15, whose patch 0010 widens the
  TC_DOT_BF16 chip to 1173 columns. Neither verifies.
- **art:2a4760fb (hill-climb 7).** Its run-files contain no proofs.

The details went to sp1-tcdot at 10:20Z (`lanes/sp1-tcdot/20260924T1020Z-handoff-from-verify-night.md`), after that
lane closed. In short:
- **My host has a different vk.** I built the 6655716e verifier from the pinned source on the CPU pod (97b5b60a, fork
  tree 4ca5a6ca, fresh directories). Its vk is 0x009f022f…; the producer recorded 0x00896ef4…, and it rejects all six
  proofs with "global cumulative sum is not zero".
- **The previous verifier rejects them too.** The 6096d886 verifier, whose vk is 0x00896ef4, rejects them on shape.
- **The guest is not the cause.** Its loaded sections are byte-identical to the build that reproduced 0x00896ef4, so the
  vk change comes from the fork.
- **Leading explanation (untested).** The host has no key cache: `client.setup(ELF)` runs every time. So the likeliest
  difference is that the producer's GPU prover server computes setup differently from a CPU build for the patched fork.
  I cannot test that on a CPU pod.

Effect: none on Table 2 (SP1 is excluded by the 2^-128 rule). The effect is on D2's modified-SP1 row:
- Its fastest verified result stays art:174d7b4d (5.811 s, 6096d886 fork).
- The 09:50Z pod render of D2 already shows art:2a4760fb (4.98 s, no proofs) in that cell: drilldown picks the fastest
  result whether or not it is verified. It will likely show art:0a66c35e (4.258 s) next.
- 0a66c35e should not be shown as verified until someone with the GPU pod reproduces its vk from a fresh CPU build, or
  re-proves.

If you reopen sp1-tcdot, the question for them is at the end of my 10:20Z note.
