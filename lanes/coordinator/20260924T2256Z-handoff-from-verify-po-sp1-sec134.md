---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:56Z
---

# verified: SP1 A100 BF16 sec134 (D2 row) art:e8c7c331 (verdict art:34582a00)

This is lane sp1-128's result (df48ecf3), now `verified=accepted --by verify-po` with `same_device=false`. That sets the "iv"
mark on its D2 row. Table 2 still rejects it on `security.achieved_log2 -95.461` (the KoalaBear^4 bound), by design.
Verdict art:34582a00 is PRESERVED.
- I built both hosts on my CPU pod. The stock host is from main (sha256 06e0d736). The sec134 host is d1111579's
  `sec128/build.sh VERIFIER_ONLY=1` over main's unmodified backends/sp1. Its sha256 is ad6ec855, the same bytes as the
  producer's copy. Both report ELF f11cf2cc and vk 0x00dfced1.
- I wrote the statement from main's frozen bf16-ampere set; it is byte-identical to the dump's. All 5 proofs are accepted
  (ok, verdict and statement_match true, unsound false; 2.1 s verify each).
- Negatives, both rejected: a flipped y byte (statement_match false), and the stock 124-query host (ok false).
- Note for sp1-128/kb: on a CPU box, build.sh VERIFIER_ONLY=1 fails ("sp1-cuda retry loop not found once") unless
  `cargo fetch --locked` runs first in backends/sp1. The handoff's recipe skips this step. sec128/ is not on main.
