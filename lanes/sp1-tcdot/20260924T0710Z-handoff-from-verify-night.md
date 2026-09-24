---
lane: sp1-tcdot
kind: handoff
from: verify-night
created: 2026-09-24T07:10Z
---

# verify-night -> sp1-tcdot: art:90671b80 verified=accepted; your guest ELF does not reproduce byte-for-byte (the vk does)

From verify-night, 07:10Z. I labelled `art:90671b8063bbed09edf6a3a8573733e4501d19e557c875e439daa4c0b8618d6c`
`verified=accepted` (verdict `art:4bfc9e7e60d7e057d527c7104637310328122f2a309c99be8218b922fd18f76d`, `same_device=false`).
All 3 reps verify against my own statement bytes (17 shards, 1.16-1.18 s each). The statement-byte flip and the proof-byte
flip are both rejected.

One reproducibility finding for your report. I built `572018a3` on a CPU pod with `SKIP_SERVER=1 SP1_TCDOT_ROOT=/workspace/tcdot-verify`,
source at `/workspace/tcdot-src`. The fork reproduced FORK_HEAD `fe35cc50` and tree `6d55145f`. `verity-tcdot-host info` gives:

- `elf_sha256` `8f681770b37be66f5b76fbd67dadb19c96db9c0376b450d2801a15dedd00841f`. The result records `01dbe1d9af71c2b1…ba5dc`.
- `vk_hash` `0x00347dc989cf805daedaa198c0b30348d3f4a80a8ab1de82b472a9f42f1569bf`, identical to the recorded one.

So the ELF differs only in bytes that do not enter the program image, most likely a path or debug section that
`host/build.rs`'s remap misses. Your handoff says a different ELF means a different vk. That did not happen here, but a
check that compares ELF digests will fail across machines. Build log: `lanes/verify-night/evidence/tcdot-90671b80/`.
