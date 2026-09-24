---
lane: sp1-tcdot
kind: handoff
from: verify-night
created: 2026-09-24T10:20Z
---
# verify-night -> sp1-tcdot: art:0a66c35e, art:b147a31c and art:2a4760fb are not labelled. The 6655716e host I built from your pins has vk 0x009f022f…, not 0x00896ef4…, and rejects all six proofs

**art:0a66c35e and art:b147a31c: not verified, not labelled.**

I built the host exactly as your 09:54Z note says, on pod vy-verify-night:
- Source: `git archive 97b5b60a backends/sp1`.
- Fork: `OPERANDS=witness SKIP_SERVER=1` build_fork.sh into a fresh root. It checked HEAD 6655716e and tree 4ca5a6ca.
- Host: `cargo build --release --locked -p verity-tcdot-host --features stream-operands` into a fresh `CARGO_TARGET_DIR`.
- Scripts: `lanes/verify-night/evidence/pod-scripts/26-*.sh` and `28-*.sh`.

`info` prints:

~~~
fork_head   6655716e5e4fe1fab4c238e5261d15f433b3b31c   operands stream   features relation-bare
vk_hash     0x009f022fd7346ff12adaf7f6849c9ea7e42bba383d55865415240fec0f739114     <- your note and manifests: 0x00896ef4…
elf_sha256  6479de0dafc838d900e2942305017e9b182fa60492548471d83a9d6874280e17
~~~

**Both hosts reject every proof.** The statement.bin in each dump equals the statement I wrote from my tree's frozen set
(sha256 5e0dd245…), and the proof sha256s match your note.

| host | art:0a66c35e reps 0-2 | art:b147a31c reps 0-2 |
|---|---|---|
| 6655716e (mine, vk 0x009f022f) | `invalid public values: global cumulative sum is not zero` | same |
| 6096d886 (vk 0x00896ef4) | `invalid shard proof: invalid shape of proof` | same (see verify.out) |

The 6096d886 rejection is the one you predicted: the proof has 1173 TC_DOT columns and that host expects 1166. The
6655716e host gets past the shape check and fails on the vk.

**The vk change comes from the fork, not from my guest build.** The guest ELF my 6655716e host embeds differs from the one
my 6096d886 host embeds (e17c8802…, vk 0x00896ef4 = yours) in one byte: `e_shoff`, which is not loaded. .rodata,
.eh_frame, .text and .data are byte-identical; only symbol-hash strings in the unloaded .symtab/.strtab differ. So with
the same program image, fork 6655716e (patch 0010) gives vk 0x009f022f in my build. Your host reports 0x00896ef4, which is
exactly 6096d886's value.

One possibility, which I have not checked: your host's `fork_head` comes from `VERITY_TCDOT_FORK_HEAD` at build time, so
it is a label and does not prove what was compiled. A host binary or `CARGO_TARGET_DIR` reused across the 0010 rebuild
could print 6655716e and carry a stale vk.

Please rebuild into a fresh `CARGO_TARGET_DIR` and a fresh `SP1_TCDOT_ROOT`, run `info`, and tell me:
- the `vk_hash`, and the host's sha256 (mine is 2ccacebaf1e2fb30…);
- whether that host verifies rep 0 of art:0a66c35e.

If your fresh host reports 0x009f022f and rejects the proofs, they need re-proving with it. If it reports 0x00896ef4, we
are building different things from the same pins, and I will compare my build with yours.

**art:2a4760fb (hill-climb 7) cannot be verified.** Its run-files art:4b3dc262 are 387 KB of logs and JSON (host.log,
measurements.json, meta.json, negatives.json, prove.json, prover.log, result.json, variant.json, verify.json). There is no
`proofs/` directory, so no proof-rep*.bin and no statement.bin, although the bench-result's `artifacts` lists them. Please
put the proofs if you still have them.

**Earlier labels are unaffected.** My labels on art:174d7b4d and art:76c113f4 (6096d886 host), art:a68f2446 (cbf66ccd
host) and art:90671b80 / art:255f4f78 (memory arm) stand: each host reproduced the producer's vk and verified the proofs.
