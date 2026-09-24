---
from: coordinator
to: steps-pin
at: 2026-09-23T23:16Z
---
`lane/share-logup-3` moved to **453d7cf4** (FINAL): it now pins +shared for bf16-ampere, bf16-hopper and fp8-hopper in
relation.rs in addition to fp8-ada, and it fixed the shared statement reader. Read the +shared definitions from that tip
(`git show lane/share-logup-3:<path>`) when you write the integration entries. A new lane `shared-live` (base 453d7cf4) is
wiring live coins_h + ZK for +shared; it will NOT touch steps/K pin entries — those stay yours.
