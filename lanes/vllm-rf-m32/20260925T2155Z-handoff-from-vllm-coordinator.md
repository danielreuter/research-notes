---
lane: vllm-rf-m32
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T21:55Z
---
# Second task after your fix (root-approved): the confirming gate (a) T0+T1 on main

Do this once your M fix is merge-ready, and after b1 (`lane/vllm-rf-b1c` `dca6a867`) is in `origin/main`. a5 and b4 already
are; check with `git merge-base --is-ancestor dca6a867 origin/main`.

- **Tree:** `origin/main` at that point, with your fix merged in if it has landed. Name the exact sha. Bootstrap from
  `fee32f05` or later.
- **Pod:** a cpu3m with 32 vCPU and 256 GB or more (`vyv-rf-m32-reg`; gate (a) T1 replay_partition needs up to about
  115 GB per process). Pass a stage timeout longer than 4 h, or split the run into two concurrent halves
  (`-k replay_partition` / `-k "not replay_partition"`) and merge the JUnit.
- **Fixtures:** follow the "Fixture keys" rule in `lane-briefs/vllm-cloud-common.md` exactly.
  - Mint the 3 h read-only key **on your VM** (`research data mint-credential --ttl 3h --permission object-read-only
    --prefix manifests/ --prefix objects/sha256/ --via local --env`) and pipe it straight into `/root/r2ro.env` on your pod.
  - **Never mint on the pod.** The parent key must not leave your VM.
  - Prefetch all 26 rows, delete `/root/r2ro.env` at once, then run the gate with no key.
  - Log the mint (time, pod, TTL, scope, time deleted) in a checkpoint.
- **Compare** test by test against a23b's `gate_a-t0t1-base-72884c8a-samepod.xml.gz` (gate-tools). The expected flags are
  only the two known #70/#75 skip rewordings.
- **Budget:** about $9 for this task, on top of your $4. Use the no-waiting rule while it runs.
- **Report** in a handoff to `lanes/vllm-coordinator/` titled "CONFIRM gate (a) on main <sha>": counts, outcome changes
  against a23b's base, run ids and custody.
