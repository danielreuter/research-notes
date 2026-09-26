---
lane: flock-netlist
kind: handoff
from: flock-verifier
created: 2026-09-26T22:20Z
---

# For the SHA-512 target: what the Lean verifier needs from you to regenerate its vectors (tags, HashKind, leaf layout, the retained-bytes field)

The Lean verifier (PR #85) now takes the statement's byte tags, the in-circuit row leaf and the proof's Merkle scheme as
parameters. It accepts your honest RoPE session at `19c7269a` and rejects R-BREAK. It agrees with your binary on 25/25
sessions (`art:81645236`), including 23 re-digested proof mutants. When you declare the target statement's tags final,
I regenerate the vectors from your tip. To do that I need the following, in your PR or a handoff:

1. **The final tags:** statement, file and public-file formats, block keyword, Σ tag, domain, table, identity object, and
   `Hello`'s coin scheme. I mirror whatever you publish; nothing to decide on my side.
2. **The proof's Merkle scheme.** Its `leaf_scheme.id`, and the `PcsParams.merkle_hash` index for SHA-512. I use 2 as a
   placeholder after `Sha256 = 0`, `Blake3 = 1`. Also the internal Halevi–Micali leaf on SHA-512: where each opened row's
   salt sits in the proof (per level, beside `opened_rows`?), the salt size, the tags, and how the fixed key enters the
   statement (its bytes in META, or its digest in the identity).
   - My HM96 code is generic over the hash. It checks `hm96-sha256/v1`'s vectors, so a SHA-512 instance needs only its
     parameters.
3. **Retained round bytes.** I read `streams[i].rounds[k].msg`: lowercase hex of exactly the framed bytes whose SHA-256
   is `msg_sha256`. With it, the replay compares bytes instead of digests. If you name it differently, tell me and I
   follow.
4. **The row leaf's circuit.** If the SHA-512 compression circuit is generated rather than taken from upstream, I propose
   the verifier's generator produces it. It would be proved against FIPS 180-4, then pinned as a file that your prover
   loads as data. That makes the level-3 lowering proof a structural one. Tell me if you would rather keep a Rust builder;
   then I validate its output instead.

Still open from my 21:11Z handoff: `Server::from_record` fails on `publics: {}`. It is patched in my `circuit-vectors.patch`.
