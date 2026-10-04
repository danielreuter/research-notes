---
id: proofs-20261004T0515Z-friction-lean-build-oom-16gb
campaign: soundness
lane: proofs
kind: friction
status: open
repo: verity
origin: bc-8416bc72
---
Building `FlockSoundness` (`backends/flock/verifier/lean/soundness`) on a 16 GB cloud-agent VM is OOM-killed (exit 137) at `FlockSoundness.Refine.Setup`, which peaks at about 15 GB resident (about 9 GB resident plus 7.5 GB swapped in one measurement). Two lanes hit it independently on Oct 4 (scope-a bc-618959ec, scope-ef bc-5c4068e2) and each lost a build before adding a 24 GB `/swapfile`, after which it built in 852 s. Neither VM had a notes tree to record it. Fix candidates: the environment's VM size or a swapfile in the environment setup, or a line in `.agents/skills/lean-proofs/SKILL.md` telling lanes to add swap before a local soundness build. Workaround: `sudo fallocate -l 24G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`.
