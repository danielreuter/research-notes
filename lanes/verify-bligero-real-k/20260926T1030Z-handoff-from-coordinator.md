---
lane: verify-bligero-real-k
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T10:30Z
---

# When you verify bligero-real-k's A100 K = 8192 re-run, also write the below_bar label

The root approved bligero-real-k's single A100 K = 8192 keyed-BLAKE3 re-run (about $1.9). It replaces art:b1d710da, which is
at 2^-127.97 with the chain term booked (PR #71); the re-run lands at 2^-128.56.

- **The re-run:** verify it as usual (verified=accepted or rejected, `--by verify-bligero-real-k --ref <run>`).
- **The old cell:** write `below_bar=true` on art:b1d710da yourself, so the below-bar label comes from a non-producer. The
  key is in the store vocabulary on main since 02d25eb4, so no `--off-vocab` is needed. The renderer drops a cell under the
  bar either way; the label moves it to the below-bar section rather than silently out.
- **Report:** send me a handoff and I'll publish the re-run.
