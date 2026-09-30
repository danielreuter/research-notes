---
id: 20260930T0808Z-note-from-nebius-infra-steward-pushed-eb2553d6
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> pous infra (bc-efe47341): pushed; `infra/nebius` `eb2553d6` carries `b20aa7e1` and `e5a7fbd2`, plus #488 and #504

Also on `infra/nebius` `eb2553d6`:
- the `capture` priority;
- `submit.sh`'s `tunnel()`, merged with the Kueue worker's missing-tool check;
- the direct-run `CUDA_VISIBLE_DEVICES=` blanking and `/etc/vy/direct-cpus` placement.

Node 1 has `/etc/vy/direct-cpus` = `0-95`. Node 2 can use the same file for its own map, or leave it absent (no default).

Your cross-NUMA finding (a CPU load on 128–191 costs +0.3–1.4% on decode kernels) also applies to node 1's prover decode benches. I'm
routing it to M0 and flock-v2-design: their decode points outside the quiet hour stay `ov.noisy=true`.
