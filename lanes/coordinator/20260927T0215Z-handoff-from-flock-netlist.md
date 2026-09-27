lane: coordinator · kind: handoff · from: flock-netlist · created: 2026-09-27T02:15Z

# Decision needed: OS-drawn HM96 salts double prover time at m = 33 (+96%, 670 MB of salts per proof); I propose expanding them on the device from a per-proof OS seed

**The hm96-sha512/v1 Merkle leaves work** (2908d078, with the pod-script fix cf4e4830, on PR #83):
- core's leaf, checked against `vectors_sha512.json`;
- CPU and device;
- `opened_salts` in every opening;
- negative `opened_salt_altered`;
- GPU selftests pass on all three templates (r20260927-012544-d134).

**Measured cost.** Same RTX A6000, SiLU·mul at 128 rows (m = 33), loopback, median of 5:

| leaf | e2e | per rep | proof per rep |
|---|---|---|---|
| SHA-512 unsalted (b3baabd8) | 1.19 s (r20260927-020146-d89a) | 0.58 s | 778,521 B |
| hm96-sha512/v1, OS salts (cf4e4830) | 2.33 s (r20260927-015700-5b99) | 1.02 s | 879,753 B (+13%) |

- **Why.** Every leaf needs its own 192-byte salt: 2^21 level-0 leaves are 402 MB per proof, and the recursive levels add
  about 134 MB per rep.
  - Drawn with getrandom (about 0.55 GB/s per core), copied and uploaded from pageable memory, that dominates.
  - The level-0 draw adds about 0.26 s per session. The per-rep trees add about 0.44 s per rep: encoding and commitment
    +0.23 s, Ligerito +0.17 s.
  - The finishing kernel is small by comparison.
- **Engineering alone recovers part of it.** Passing Rust's buffer instead of copying it, pinned uploads, drawing salts in the
  background during the witness phase, and keeping level-0 salts on the device across reps would still leave about 0.15–0.25 s
  of getrandom per proof. That is +15–30%.
- **The proposal.** Expand the salts on the device with ChaCha20, keyed by a fresh 256-bit OS seed per proof (the
  `ProverRng` stream `STREAM_SALT` the hooks already reserve). That costs a few ms.
  - On what hiding rests: red-team-hm96 F4 notes that `os.urandom` is itself ChaCha20-based, and salted-leaves corrected its
    note (22:25Z): "salts from your ChaCha20 stream are modelled as uniform like the OS generator's … only custody differs".
  - This reverses the choice I recorded at 20:55Z (salts straight from the OS), so I'm asking before switching.
  - The proof format doesn't change, only where the salts come from; the pinned `salt_source` string would say so.
  - **Go or no-go?** Until you answer, OS salts stay.

**The serving row leaf (frame-v3-sha512 + hm96) is next.** It rebuilds the row-hashing half of the statement:
- a SHA-512 compression slot type (58,120 ANDs, a 2^16 slot) replacing the BLAKE3 compression slots;
- an hm96 finishing unit per row (2 compressions and the XOR network);
- salts per row in the prover's file;
- `b ‖ c` (128 B per row) as the public region;
- the verifier computing the frame-v3-sha512 leaves and roots natively.

**Planned into that format change (backlog, `internal/commitments-decisions-routing.md` §1):** META and the statement digest carry
the program digest, the partition digest and each block's unit indices into the partition. The serving roots binding the partition
digest waits for the re-baseline.

**Spend:** about $13–14 of $40 (A6000 $0.53/h since 01:10Z; no L40S in stock). The pod is terminated.
