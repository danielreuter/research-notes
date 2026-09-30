---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: sm_120 PoUW coordinator (bc-2aa33ad8)
created: 2026-09-30T06:25Z
---

# -> bc-2aa33ad8: Pearl-C's sm_120 hashing options are priced

- **The report:** `internal/pouw/hashing-sm120-options.md` in the project store. It builds on GPU 2's counts and issue models,
  with no GPU used. It prices each option at both headlines, classes each as a kernel win or a protocol change, and names
  the assumption rows each touches.
- **Prefill 8,192³.** Hashing is about 0.41× the plain GEMM today at 1× issue (0.21× at 2×).
  - Overlapping the epilogue hashing with the mainloop is a kernel win, about −0.20 to −0.27×.
  - A protocol bundle takes it to about 0.07–0.10×, for a total of about 1.10–1.39×. The bundle is BLAKE3 for the digests,
    U-only messages, BF16 A rows and tree-mode commitments.
- **Decode m = 32: a blocker.** `audit.commit_rows` commits A as SHA-256 over each whole row, and Pearl-C reuses it. That is
  513 serial compressions per 32 KB row before forming can start: about 0.4–0.7 ms against a 42 µs GEMM.
  - #449's device bench models TurboSHAKE128 1 KB segments instead, which the verifier doesn't accept.
  - A BLAKE3 tree commitment (P4), plus the post-GEMM hashing on a side stream, brings decode's hashing to about
    0.29–0.55×.
  - Please route P4 to #449's owner and the theory lane before decode attempts count.
- **Your calls:**
  - one hashing-format version bundling P1, P3, P4 and P5;
  - a dependent-chain decode method in GPU 6's harness for arms that overlap across calls;
  - whether `pearl-c-sm120` needs Pearl's lottery tickets (nothing in PoUW's audit reads them).
- **Fill candidates:** five GPU checks, each `gpu-lease 1`, restartable and extending GPU 2's tree, are in the report's §6
  for you to compile into `rtx-pro/fill-candidates.md`. That file is yours, so I haven't edited it.
