---
id: 20260930T2226Z-handoff-from-old-circuits-and-proofs-replay-bundle-retention
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Replay bundles are filling node 1's disk (#599)

@infra (Slack 1790807092.688879): node 1 is at 76% disk and growing about 190 GB/h. /workspace/jobs/cov holds 131 GB.
cov-g142's TinyLlama B8 bundle is 45 GB (store/raw/s0.bin is 36 GB). The Phi-3 B8 .partial bundles run 11-60 GB.

Please put the following on #599's next head, in code:
1. Delete a bundle once its replay record is committed (#598's `row stage replay` success path, or a `--keep-bundle` flag).
2. Delete the .partial bundle when a deferred Commit fails or is interrupted (a finally/atexit handler that removes the partial directory).
3. Add a per-node cap on unreplayed bundle bytes (default 300 GB): refuse a new `--replay-deferred` Commit by name when it is exceeded.
4. Explain why the bundle carries the whole raw store (36 GB), rather than only the members the 460 sampled units open plus their Merkle paths. If the replay needs only the opened members, bundle those; a B8 bundle should then be well under 1 GB.

Until then: no new B8 `--replay-deferred` Commits on node 1. Keep only the newest complete Phi-3 B8 bundle, for the #599/#598 acceptance probe. Tell @infra which others are safe to delete; I told them any .partial is.

Reply as a -handoff- in lanes/old-circuits-and-proofs/.
