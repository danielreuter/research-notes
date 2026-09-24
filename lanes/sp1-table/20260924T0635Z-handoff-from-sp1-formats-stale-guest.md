---
lane: sp1-table
kind: handoff
from: sp1-formats
created: 2026-09-24T06:35Z
---

# pod_bootstrap.sh can install a host whose embedded guest is from an older source tree

Seen on vy-sp1f-4090 (target `/workspace/sp1-target-cuda-relation-bare`), research runs r20260924-061921-ce22 (src
0aa310e9) then r20260924-062533-e7c9 (src 0f14268c, which changes `common/src/tc_fp8.rs` and friends): the second run
printed `veritor-zk-guest built at 2026-09-24 06:20:40` (the first run's time) and the same `elf_sha256 722e1e03...`.

Why: `sp1_build` emits `rerun-if-changed` with ABSOLUTE paths, and the host's build-script output records them for
the first source dir:

~~~
cargo::rerun-if-changed=/workspace/research/src/0aa310e9.../backends/sp1/guest/src
cargo:rerun-if-changed=/workspace/research/src/0aa310e9.../backends/sp1/common
~~~

Each `research run` ships to a new `/workspace/research/src/<sha>/`, but the target dir is persistent and cargo's own
fingerprints (package-root-relative) consider the host build script fresh, so `build.rs` never reruns and the guest
is never rebuilt for the new tree. The host crate itself does recompile, so host-side `decide` and the embedded guest
can disagree; the identity in the fingerprint is then the old guest's, not the recorded `source_sha`'s.

The sound guest is protected by the approved-identity check. The `relation-bare` host has no such check.

What I do for my cells: before `pod_bootstrap.sh`, delete `$CARGO_TARGET_DIR/release/.fingerprint/veritor-zk-host-*` and
`$CARGO_TARGET_DIR/release/build/veritor-zk-host-*`, then confirm that the printed `elf_sha256` changed. If your A100
host was bootstrapped more than once from different source dirs in the same target dir, it's worth checking the build
timestamp line in the bootstrap log against the commit you record. A durable fix is yours to choose; for example,
`pod_bootstrap.sh` could remove those two globs whenever `$HERE` differs from the last build's source dir.
