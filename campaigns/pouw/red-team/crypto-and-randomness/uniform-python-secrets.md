---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `uniform/python-secrets`: A

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** The verifier's 32-byte source, drawn from the OS CSPRNG once per window after the receipt, is uniform and fresh. Used by sampled proofs' `Ledger` and the one-stage audit, not by `pearl-c-*`.

- Python's `secrets` reads the kernel CSPRNG (`getrandom`), the standard source for keys. The residual risk is the platform's entropy at boot, which is the same for every key on the host.

**Rating.** **A.**
