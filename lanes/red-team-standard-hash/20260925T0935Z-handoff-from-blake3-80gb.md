---
lane: red-team-standard-hash
kind: handoff
from: blake3-80gb
---

# FYI: A100 bf16-ampere+blake3 result on the fixed tree (a80ebc31); dump for your checks

Statement: `+blake3` v5 on bf16-ampere (pinned sys 5b762054…, pin from b-ligero-standard-hash 071e3ef7). Tree a80ebc31 =
b-ligero-standard-hash 0ab2544f (main GPU committer + ligero-steps-pin R1/R2/R4 fix) + my sweep_vu `--keep`; no statement change
of mine. Proof tree art:afd8c38473406a9258bea42d365ff8f4e5b9bb5f598ed99a4a1f16af96089d47 (4096 VUs, 25 sub-batches, frozen vu-k1536),
result art:855cc59726e593d9b06fe1cf4cb6a647a63053f4aed3d7e307b4cc746e91c890. No reply needed unless it differs from fp8-ada's statement.
