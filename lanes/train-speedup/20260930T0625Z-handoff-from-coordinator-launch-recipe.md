---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: train-speedup
kind: handoff
from: coordinator
created: 2026-09-30T06:25Z
---

# The coordinator's train launch recipe, and where train time goes

For the "Cut merge-train time on Nebius" worker. Send merge requests for fixes to the coordinator; they go ahead of other trains.

## How a train runs today

1. Build `tr-<L>` in a worktree on current `main`: `git merge --no-ff` each PR head in order.
2. Pre-lint it locally: `tests/test_no_wall_clock.py`, `tests/test_repository.py`, and `integrations/vllm/tests/lint` for vLLM trains.
3. Launch the full check with `/tmp/launchv.sh tr-<L> <L> <machine> [send]`. It prints `RUN <run id>`.
4. Precompute the merge commit with `/tmp/mkmerge.sh <main> <train tip> <L> <run id>`. This creates the `mm-<L>` branch.
5. Poll with `research fetch <run id>`. On a pass, run `research merge <tip> --remote no-sweep -m "Merge train <L> (<sha8>)"` with `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` set to `2026-09-28T23:00:00+0000`. The result must equal `mm-<L>`. Then check that `origin/main` is an ancestor and push fast-forward.
6. **Serialization cost:** a train that lands second must have the new `main` merged in and be re-checked. That's a whole second check. Sometimes I restart a queued train's check on the new `main` to avoid it.

## Knobs, all opt-in

| Knob | Effect |
|---|---|
| `VERDICTS=<verdicts.tar.gz>` | Send a passing check's verdict pack (`--verdicts-in`). Suites whose key matches are reused. Required, or set `NO_VERDICTS=<why>`. I use `/tmp/verdicts-all.tar.gz`. |
| `KEEP_GOING=1` | `check.py --keep-going`, for trees with #438, which otherwise stop at the first failure. |
| `send` (4th arg) | Send the pinned upstream build and inputs for `lean-agreement`. A merge that changes `backends/flock/` needs it. The launcher's AVX-512 guard is stale: the preflight now says the x86-64-v3 build needs no AVX-512. |
| `NEBIUS_SLOT=a` or `b` | For vy-nebius-1 (nebius-infra steward 06:27Z: **never `gpu-lease`**; it blocks the GPU cutover and exits 2 after it). Wraps the check as `flock /workspace/research/locks/check-a.lock taskset -c 128-159 …` (slot a) or `check-b.lock` with 160–191 (slot b). That gives two parallel 32-vCPU CPU-only check slots, each serialized by its own lock. It also sets `RUN_PATH`, `SKIP_CLEAN=1` and `CPU_ONLY=1` (`--env CUDA_VISIBLE_DEVICES=`), plus `--env UV_PYTHON=3.14.7`, as you asked. `check.py` sizes its jobs from `os.sched_getaffinity`. The launcher refuses any `WRAP` containing `gpu-lease`. A step that truly needs a GPU goes through the steward for a Kueue `prover-dev` slot. |
| `RUN_PATH=/home/research/.local/bin:/home/research/.elan/bin:/home/research/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` | Sets PATH for this run only (preflight and runner, via `--env`). `~/.local/bin/uv` is 0.12.20, the preflight's pin; `/usr/local/bin/uv` is 0.12.21 and root-owned. Other lanes' PATH and suite keys stay unchanged. |
| `SKIP_CLEAN=1` | Skip deleting idle `src/*` trees, which on a shared host belong to other lanes. |

vy-nebius-1 setup, for the `research` user only: `pod_setup.sh` was run with `UV_VERSION=0.12.21` to install elan with Lean v4.34.0 and cargo, and uv 0.12.20 went into `~/.local/bin`. Nothing outside `/home/research` changed. **Update 07:13Z (root):** the two check slots are on NUMA node 0, CPUs 32–63 and 64–95. The earlier 128–191 overlapped the Build lane's pinned benchmark (128–159) and M0's (144–191), which corrupted both lines on Daniel's plots. Original allocation (research-notes `lanes/coordinator/20260930T0627Z-handoff-from-nebius-infra-steward-checks-drop-gpu-lease`). Ask the steward there if you need more.

## Where the time goes (step wall times, seconds)

| Run | Train | pytest | circuit-check | lean-suites | lean-build | total |
|---|---|---|---|---|---|---|
| r20260930-052233-0a1d | TNB, tools-only, t10 | 873 | 25 | 486 | 23 | about 16 min |
| r20260930-053952-6795 | TVE, vLLM, t10 | 1010 | 421 | 474 | 23 | about 21 min |

- The slowest suites (TVE's `suites.json`) are **verity-vllm at 876 s**, then verity at 51, verity-circuit-check at 50, verity-numerical at 46, research at 34, and the rest under 16. `suites-lean.json` has **verity-flock at 470 s**. The vLLM and flock suites are the whole critical path. pytest and lean-suites appear to run one after the other.
- circuit-check takes 25 s with a warm cache (1,110 hits) and 421 s when a train changes Definitions (TVE).
- `test_tp_moe_members::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound` takes about 50 min per row on pre-#443 trees, per the vLLM coordinator. Standing rule: never run it in two trains at once.
- Lean re-hashes, such as TLN's `tools/lean/audit.py --build --update` on t7, took about 30 min per attempt.
- Launch overhead is 40 to 210 s per launch: the source push, fetching the upstream build when `send` is used, the lean-deps URLs, and the disk-cleanup ssh.

## Pitfalls seen today

- Killing a check means killing the **workload's** process group. The harness starts `uv run … check.py` in its own session, so `kill -- -<runner_pid>` leaves it running.
- A killed check leaves `~/.cache/verity-check/lean-audit-scratch-*` behind (26 GB on t7) and empties `lean-deps`. The next preflight then asks for 86 GB for 3 dependency restores and refuses the 100 GB RunPod pods.
- The preflight pins the exact uv version (0.12.20), so a host with a newer uv fails preflight.

## The launcher (`/tmp/launchv.sh` on the coordinator VM, as of 08:10Z)

~~~bash
# usage: launchv.sh <train branch in /workspace> <label> <pod> [send]
# Recorded train launch from the coordinator VM (root 16:35Z): custody on, the store-backed tests run, never skipped.
# The control pod's r2.env is a temporary credential and cannot mint the custody key, so trains launch here, with the parent key.
set -u
B=$1; L=$2; P=$3; SEND=${4:-}
cd /workspace
export PYTHONPATH=tools/research/src RESEARCH_MACHINES_D=/tmp/machines.d
[ -n "${VERITY_SKIP_STORE:-}" ] && { echo "REFUSED: VERITY_SKIP_STORE is set: a recorded train runs the store-backed tests"; exit 1; }
[ -n "${AWS_SESSION_TOKEN:-}" ] && { echo "REFUSED: AWS_SESSION_TOKEN is set: a temporary credential cannot mint the custody key"; exit 1; }
[ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${R2_ENDPOINT:-}" ] || { echo "REFUSED: no parent R2 key in this shell (Cursor secrets)"; exit 1; }
W=/tmp/src-$L
rm -rf $W; git worktree prune; git worktree add -q --detach $W $B || exit 1
(cd $W && timeout 300 uv run -q pytest -q -p no:cacheprovider tests/test_no_wall_clock.py 2>&1 | tail -1) | grep -q " passed" || { echo "REFUSED: wall-clock lint failed on $B"; exit 1; }
AF=()
# verdict packs to every check (Daniel via root 20:16Z, change 1): VERDICTS=<a passing check's verdicts.tar.gz>, or NO_VERDICTS=<why>
VIN=""
[ -n "${KEEP_GOING:-}" ] && VIN=" --keep-going"   # only for trees with #438 (fail-fast): a stopped step stores no verdict
case $L in TB|TM|TO|TU|TX) NO_VERDICTS=${NO_VERDICTS:-built before the 20:16Z policy};; esac
if [ -n "${VERDICTS:-}" ]; then
  [ -s "$VERDICTS" ] || { echo "REFUSED: VERDICTS=$VERDICTS is not a file"; exit 1; }
  AF+=(--send "$VERDICTS"); VIN="$VIN --verdicts-in $(basename "$VERDICTS")"
elif [ -z "${NO_VERDICTS:-}" ]; then
  echo "REFUSED: no verdict pack: set VERDICTS=<verdicts.tar.gz of a passing check> (or NO_VERDICTS=<reason>)"; exit 1
fi
if [ "$SEND" = send ]; then
  for k in upstream inputs; do
    a=$(python3 -c "import json;print(json.load(open('$W/backends/flock/verifier/upstream.json'))['$k']['art'])")
    h=$(python3 -c "import json;print(json.load(open('$W/backends/flock/verifier/upstream.json'))['$k']['sha256'])")
    f=$(timeout 900 python3 -m research data fetch "$a" 2>/dev/null | tail -1)
    [ -f "$f" ] && [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$h" ] || { echo "REFUSED: $k $a missing or sha mismatch"; exit 1; }
    AF+=(--send "$f")
  done
  n=$(timeout 120 python3 -m research pods ssh $P -- "grep -c avx512f /proc/cpuinfo" 2>/dev/null | tail -1)
  [ "${n:-0}" -gt 0 ] 2>/dev/null || { echo "REFUSED: $P has no avx512f; lean-agreement needs an AVX-512 pod"; exit 1; }
fi
# presigned URLs for the pinned Lean dependency bundles (the preflight in #440 refuses a pod whose deps aren't warm without them)
LD=$(cd $W && timeout 300 uv run -q python tools/check/check.py --lean-deps-files 2>/dev/null | grep -oE -- '--send [^ ]+' | head -1 | cut -d' ' -f2)
[ -n "$LD" ] && [ -s "$LD" ] && { AF+=(--send "$LD"); echo "lean deps: sending $(basename $LD)"; }
ENVK=()
# shared hosts: NEBIUS_SLOT=a|b (vy-nebius-1, nebius-infra steward 06:27Z; NUMA node 0 per root 07:13Z, clear of the Build lane's and
# M0's pinned benchmarks on 128-191) runs the check CPU-only in slot check-a (CPUs 32-63) or check-b (64-95) under that slot's flock, with RUN_PATH and SKIP_CLEAN set; never gpu-lease (it blocks the GPU cutover and exits 2
# after it). RUN_PATH gives this run (not the host's other lanes) the user-installed uv/elan/cargo; SKIP_CLEAN leaves other lanes' trees
# alone; CPU_ONLY hides the GPUs
# until #504 lands (root 08:01Z): the check sees no host lease (LEASE_DIR) and no host deadline (/etc/research/deadline), as #504's fixture does
CLEANHOST="env -u LEASE_DIR LEASE_DEADLINE_FILE=/nonexistent/research-deadline"
case ${NEBIUS_SLOT:-} in
  a) WRAP="flock /workspace/research/locks/check-a.lock $CLEANHOST taskset -c 32-63";;
  b) WRAP="flock /workspace/research/locks/check-b.lock $CLEANHOST taskset -c 64-95";;
  c) WRAP="flock /workspace/research/locks/check-c.lock $CLEANHOST taskset -c 8-31";;   # root 08:07Z, steward backlog item 6; 0-7 stay k3s's
  '') ;;
  *) echo "REFUSED: NEBIUS_SLOT is a, b or c"; exit 1;;
esac
if [ -n "${NEBIUS_SLOT:-}" ]; then
  RUN_PATH=${RUN_PATH:-/home/research/.local/bin:/home/research/.elan/bin:/home/research/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}
  SKIP_CLEAN=1 CPU_ONLY=1
  ENVK+=(--env "UV_PYTHON=3.14.7")   # the RunPod pods' interpreter, so node 1 hits their uv cache (train-speedup)
fi
case ${WRAP:-} in *gpu-lease*) echo "REFUSED: no gpu-lease for checks (nebius-infra steward 06:27Z); use NEBIUS_SLOT=a|b"; exit 1;; esac
[ -n "${RUN_PATH:-}" ] && ENVK+=(--env "PATH=$RUN_PATH")
[ -n "${CPU_ONLY:-}" ] && ENVK+=(--env "CUDA_VISIBLE_DEVICES=")
WRAP=${WRAP:-}
if ! grep -q CHECK_STORE_CUSTODY $W/tools/check/check.py; then
  # the tree predates #420 (check.py drops RESEARCH_* from its steps, so store_io cannot see the custody key):
  # a read-only store key for the run's length makes the store-backed tests run instead
  C=$(timeout 60 python3 -m research data mint-credential --permission object-read-only --ttl 4h) || { echo "REFUSED: cannot mint the read-only key"; exit 1; }
  while IFS= read -r kv; do ENVK+=(--env "$kv"); done < <(python3 -c "
import json,sys;d=json.loads(sys.argv[1])
for k,v in (('AWS_ACCESS_KEY_ID',d['accessKeyId']),('AWS_SECRET_ACCESS_KEY',d['secretAccessKey']),('AWS_SESSION_TOKEN',d['sessionToken'])): print(f'{k}={v}')" "$C")
  ENVK+=(--env "R2_ENDPOINT=$R2_ENDPOINT" --env "R2_BUCKET=$R2_BUCKET"); unset C
fi
# finished runs' source trees fill the pod's 100 GB disk (vy-coord-t1, 19:00Z): delete every tree no live process uses, then need 25 GB
if [ -n "${SKIP_CLEAN:-}" ]; then av=$(timeout 180 python3 -m research pods ssh $P -- 'df --output=avail -BG /workspace | tail -1 | tr -dc 0-9' 2>/dev/null | tail -1); else
av=$(timeout 180 python3 -m research pods ssh $P -- 'for d in /workspace/research/src/*/; do s=${d%/}; [ -d "$s" ] || continue; if ls -l /proc/[0-9]*/cwd 2>/dev/null | grep -qF "$s" || pgrep -f "$s" >/dev/null; then continue; fi; rm -rf "$s" && echo "cleaned ${s##*/}" >&2; done; df --output=avail -BG / | tail -1 | tr -dc 0-9' 2>/dev/null | tail -1); fi
grep -q "Lean dependency tree" $W/tools/check/preflight.py 2>/dev/null || [ "${av:-0}" -ge 45 ] 2>/dev/null || { echo "REFUSED: $P has ${av:-?} GB free after cleanup; a full check needs about 40 (TB2 and TO3 ran out at 31 and 36)"; exit 1; }
echo "disk: $P has ${av} GB free"
# a tree with #440's preflight is launched by its own research package: #448's preflight refuses a tree shipped as an archive by an
# older launcher, and the tree's own launcher ships a git checkout
LP=$PYTHONPATH; [ -f $W/tools/check/preflight.py ] && LP=$W/tools/research/src
PYTHONPATH=$LP setsid nohup python3 -m research run --on $P --project verity --source $W --cwd source --tool check --timeout 10800 "${AF[@]}" "${ENVK[@]}" \
  -- $WRAP bash -c "exec uv run --locked --extra torch-cpu python tools/check/check.py$VIN" > /tmp/run-$L.log 2>&1 < /dev/null &
for i in $(seq 1 40); do id=$(grep -h launched /tmp/run-$L.log 2>/dev/null | grep -oE 'r2026[0-9]{4}-[0-9]{6}-[a-f0-9]{4}' | head -1); [ -n "$id" ] && break; sleep 5; done
echo "RUN ${id:-none}"; grep -E "refused|rror" /tmp/run-$L.log | head -3
~~~
