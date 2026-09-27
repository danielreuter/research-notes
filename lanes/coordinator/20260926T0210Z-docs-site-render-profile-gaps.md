---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# From the docs site: where the render's backend profiles disagree with verity main

**To:** coordinator. **From:** the docs-site worker. **Written:** Fri Sep 25, 7:10 PM PT.

## Why this matters now

The docs site's Security table now comes straight from the entities JSON's backend profiles. Those are `backends[].properties` and `backends[].assumptions` in `internal/tables-render/latest.json`, rendered at 01:29Z from verity `a50a3614`. The backend family pages were written separately, from verity `origin/main` (`35560c88`).

Where the two disagree, the site now contradicts itself: a family page lists an assumption that the Security table for the same backend doesn't. The fixes below belong in the render's profiles; the site follows whatever the JSON says.

## The gaps

- **A-route-a:**
  - **The JSON:** its mapped assumptions are `cr/sha-512` plus proven bounds.
  - **Main:** the link's Fiat–Shamir coins and its root_F binding use SHA-256. In the JSON that SHA-256 claim is unmapped (`id: null`), so it drops out of the table.
  - **The fix:** map it to `cr/sha-256`, or to `random-oracle` if it's the challenge hash.
- **B-interactive:**
  - **Main:** B-Ligero's protocol says zero knowledge needs a random oracle for the unsalted Merkle leaves.
  - **The JSON:** it lists `malicious-verifier-zk` without `random-oracle`.
- **C-interactive:**
  - **The JSON:** its only assumption is `rs-proximity-johnson`, which is proven, so the site's table reads "Only proven bounds".
  - **Main:** the CPU prover's Merkle trees use BLAKE3, which is a proof-internal commitment, so `cr/blake3` should be listed.
- **The C-interactive result on the A100 (`gemm-coordinate/k1536/sm80-mma-bf16`):**
  - **The JSON:** it has a C-interactive result on this subcircuit, and it's the fastest backend there.
  - **Main:** `verity_flock` pins lowerings only for `bf16-hopper`, `fp8-ada` and `fp8-hopper`, with no Ampere lowering.
  - **Worth checking:** is the result mislabelled, or does it come from a lowering main doesn't have?
- **D-fs:**
  - **Zero knowledge:** the JSON leaves the claim unmapped ("unknown"). The site shows no zero-knowledge token for D-fs, and the family page says Verity claims none.
  - **Committed variants:** the JSON lists committed SP1 variants for which main has no guest code.
- **B-interactive rounds:** a result verified from its proof file gets 0 rounds. This is the known modelling bug. The site draws those results as derived and flags the 0 rounds until the re-render.
- **B-fs lists `honest-verifier` (rated Weak):**
  - **The render's reason:** B-fs's honest-verifier zero knowledge.
  - **The effect:** it shows as the table's one red assumption. If the rating is meant to cover only the zero-knowledge claim, not soundness, the profile may want to say so.

- **Poseidon2 rows, admissible or not:**
  - `packages/verity/src/verity/commitments/rowleaf.py` on main says Poseidon2 row leaves are inadmissible.
  - `bench/views.py` admits `frame-v3/poseidon2-babybear` and marks it `(alg.)`, and the JSON lists it with `admissible: true`.
  - The Commitments page follows the render for now. One of the two should change.

## On the site's side

- **Registry entries still missing:** ChaCha20 as a pseudorandom function, and "zero knowledge unknown". Neither is needed yet.
- **What the site does meanwhile:**
  - **Proven bounds:** it leaves out assumptions with standing `proven`.
  - **Id mapping:** it maps the render's ids to its own, for example `statistical-soundness` to `sound-statistical` and `designated-verifier` to `interactive`.
  - **Unknown ids:** it fails the build on an id it doesn't know.
