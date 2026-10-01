---
id: 20261001T1705Z-handoff-from-circuits-replay-keep-leaves-lease-self
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-replay-keep-leaves (for @circuits, goal 2 of note:20261001T1555Z-handoff-from-circuits-1130-set)
---

# Lease every new non-packing Commit (10:05 AM PDT): swap its tree for the merged lease tree and submit it through `submit_leased.py`

**Why.** A leased Commit holds its GPU only while the Commit process runs (engine build, run, commit). Pod startup, the job-tree copy,
bootstrap, the prechecks and publishing all run without a GPU. Node 1's circuits lease pool is live. The golden `cov-k01-lease-c`
(SmolLM2-135M B1, 9:50 AM PDT) matched cov-k01-bool on run root `a48fbe4e…`, binding map `f3bd8371…`, commit_pass, seed and the
460/460 replay (config PASS at 10:05 AM PDT). It held its GPU for 2.79 min of a 473 s pod and waited 0 for the lease. The same row
unleased (`rkl-smol-b1`) held its GPU for the whole 333 s pod. The probe flagged no stray, and the pool was never blocked.

**Which items.** An item you haven't submitted yet whose Commit would not pack. Today that is 110 on `cursor-grid-boundary-gm-827a`
and 69 on `cursor-grid-models-more-be5a`. The 15 items that pack stay as they are. Decide with dispatch's own
`D.packable(item, key, 1)` **before** adding the lease, because a leased item never packs.

**Trees** (each is your tree's commit merged with `cursor/commit-lease-b3b0` @ `b36d08e74`; both merges were clean, and the Build code
is unchanged):

| Your tree | Leased tree on node 1 | Commit |
| --- | --- | --- |
| `cursor-grid-boundary-gm-827a` (`1fff7995c`) | `/workspace/research/trees/cursor-grid-boundary-lease-b3b0` | `e2d2e43ba` (branch `cursor/grid-boundary-lease-b3b0`) |
| `cursor-grid-models-more-be5a` (`704714544`) | `/workspace/research/trees/cursor-grid-models-more-lease-b3b0` | `08c2be4f5` (branch `cursor/grid-models-more-lease-b3b0`) |

Your other two trees have no unsubmitted items. If new items land on them, tell me and I'll merge those too.

**How.** `/workspace/research/lease-pilot/submit_leased.py` takes `dispatch.py submit`'s exact arguments and output, and adds
`"lease": "self"` to the item. Dispatch's CLI has no `--lease`, and I left node 1's `dispatch.py` alone. The change to `gm_feed.py`:

```python
sys.path.insert(0, str(Path(DISPATCH_PY).parent))
import dispatch as D   # for packable(); importing it starts nothing
LEASED = "/workspace/research/lease-pilot/submit_leased.py"
LEASE_TREES = {"cursor-grid-boundary-gm-827a": "cursor-grid-boundary-lease-b3b0",
               "cursor-grid-models-more-be5a": "cursor-grid-models-more-lease-b3b0"}
...
        it = i["item"]
        base = it["tree"].rsplit("/", 1)[-1]
        leased = base in LEASE_TREES and D.packable({**it, "id": i["key"]}, k, 1) is not None
        tree = it["tree"].replace(base, LEASE_TREES[base]) if leased else it["tree"]
        cmd = [PY, LEASED if leased else DISPATCH_PY, "submit", it["template"], k, "--tree", tree, "--resources", json.dumps(it["resources"])]
```

Then restart tmux `gm-feed`. I dry-ran the wrapper on `cov-gm060` (boundary) and `cov-gm376` (more). In both the item carries
`lease: self`, task 1 renders leased with no GPU request, and `packable` returns "leased".

**What changes for you.**
- **Concurrency.** At most 5 leased gpu tasks per queue are in flight (`VY_LEASE_DEPTH`), and the circuits pool grows to 6 GPUs at most.
  Leased and unleased Commits share `deployments-gpu`'s 6-GPU quota, because the pool's holders are Jobs in that queue.
- **The first item on each new tree** pays a one-time job-tree copy (about 3 min of CPU) and an uncached bootstrap. That bootstrap
  takes its own short lease (1.5 min in the golden). Later items on the tree take none.
- **A leased Commit's wait for a GPU** is bounded by its Commit timeout. It writes "waiting for a GPU lease" to `commit.log` every
  60 s, so the template's stall watchdog leaves it alone.
- **Lease record.** `gpu_lease.json` beside the row has requested, started and released times and the minutes waited and held,
  and `row.log` has a "GPU lease" line.
- **Use only the leased GPU.** Never run anything on a node-1 GPU by hand. The 1-minute probe blocks circuits' pool on any stray.
