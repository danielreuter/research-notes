---
cursor:
  subagentId: "bc-d77506af-17f3-5a6e-a68a-3b2d5edeea5a"
---

# veritor → verity switchover audit (read-only, laptop, Sep 24 ~2:20 PM PT)

Nothing was edited, restarted or contacted. "Functional" means it changes which repo or code agents use. "Harmless" means it's a name only.

## 1. My Machines worker: the one that matters

**What it is.** One worker is registered: `5dae5d77-6a88-525d-825a-c2bff3e2d6a9`, display name `~/projects/veritor @ Daniel's MacBook Pro`, repo label `danielreuter/veritor`, shared assignment on. It runs as PID 15576, started Sep 23 at 2:20 PM PT, when a CLI update made the app restart it.
- The Cursor app's `cursor-agent-worker` extension spawns it from the **Agents Window's** workbench whose folder is `~/projects/veritor` (workspaceStorage `c7b93f5f…`). It's spawned with `--worker-dir ~/projects/veritor`, and its data dir is `globalStorage/anysphere.cursor-agent-worker/worker-data/cursor-agent-worker-efc76b29c6`.
- Every 10 minutes the extension re-resolves the workspace roots and re-attaches (last at 2:21 PM PT).

**Functional.** New agents land with cwd `~/projects/veritor`, a separate GitHub repo that hasn't been renamed (last push Sep 9). So:
- the workspace git repo, branch and PR target default to veritor;
- verity's `AGENTS.md` is **not** loaded, because veritor has no `AGENTS.md` or `.cursor/`;
- agents do edit veritor. There are uncommitted edits to `verity_ir/refs.py` (Sep 15), `zk/campaign/budget_cap.py` (Sep 23, 11:51 AM PT) and the untracked `accumulation/` (437 files, last Sep 23, 8:39 PM PT).

Today no live process except the worker itself has its cwd in veritor. Every lane shell is in a `verity-wt/*` or `verity-main-wt/*` worktree.

**How My Machines handles multiple repos** (from the extension's `main.js` and CLI 2026.09.23):
- Each workspace-roots set gets its own worker: name `cursor-agent-worker-<hash(roots, user)>`, its own stable worker ID, and, since the Sep 23 CLI, its own data dir and lock.
- The Sep 21 attempt at a verity worker (`c0af803a17`, repo `danielreuter/verity`) died with "another worker daemon is already running for this data dir `~/.local/share/cursor-agent`". That was the old shared-lock behaviour, and the current version no longer does it.
- Starting a worker for new roots stops only the legacy-named worker for **the same** roots, not other workers.
- **Danger:** if remote control (My Machines) is switched off in the dashboard, or Cursor signs out, the extension stops **every** worker Daniel owns (`Nge` with `ownerKey`).
- **Danger:** a Cursor CLI install or spec change restarts the worker, as happened on Sep 23 at 2:20 PM PT. Any Cursor update during live work can therefore bounce it.
- The CLI's `--worker-dir` can be repeated, but the first value is the assignment identity. Changing it means restarting the worker.
- The verity workbench in the Agents Window (`0464f5e7…`) activates the extension but cancels ("Failed to read remoteControlEnabled… Canceled"), so today only the veritor workbench runs a worker. The plain `verity` windows (6 and 7) don't run the extension at all.
- The app pushes **one** worker ID to the browser service (`setAgentPrivateWorkerId`). A second app-managed worker would therefore probably become the app's default target. Running agents stay bound to the worker ID they started on.

**Fix options:**

1. **Recommended: add a second, CLI-run worker for verity next to this one, touching nothing that exists.** In a dedicated clean checkout (don't use `verity-main-wt/main`, which is the research coordinator's merge tree):
   ~~~bash
   git -C ~/projects/verity worktree add --detach ~/projects/verity-agents origin/main
   cd ~/projects/verity-agents && cursor-agent worker start \
     --worker-dir ~/projects/verity-agents \
     --name "~/projects/verity @ Daniel's MacBook Pro" \
     --data-dir ~/.local/share/cursor-agent-verity
   ~~~
   (Run it under `tmux` or launchd so it survives.)
   - It needs Daniel's auth (`cursor-agent login` or `--api-key`), so **Daniel does this step**.
   - The repo label comes from git origin, so it becomes `danielreuter/verity`.
   - Disruption: none. It's a separate process, data dir, lock and worker ID. Check afterwards that the dashboard lists both workers, and that new coordinators or lanes are launched targeting the verity worker ID.
2. **App-managed switch.** Change the Agents Window's primary workbench folder from veritor to verity, or remove the veritor folder. **This is disruptive**: it reloads that workbench's extension host. `veritor [5-34]` (2.1 GB) is the host that `checkpoint_audit.sh` watches as the old vLLM chat's host, so reloading it may kill the chat's five subagent lanes (a1, f1, f24, f3, f56). The extension may also leave or stop the veritor worker. Do it only after those lanes finish.
3. Re-registering or restarting worker 5dae5d77 with different `--worker-dir` values: **disruptive**, because it kills the agents running on it (both laptop coordinators and a23b). Don't do this while work is live.

After the cutover, retire the veritor worker **only** when no agent is bound to 5dae5d77: close the veritor workbench, or remove the folder from it. Don't switch My Machines off, because that stops all workers.

## 2. Cursor settings

| Item | Class | Fix | Disrupts? |
|---|---|---|---|
| `User/settings.json`: no worker or veritor keys | — | none | — |
| `globalStorage/storage.json`: last-opened folder and profile map include `projects/veritor`; worker env `CURSOR_WORKSPACE_LABEL=veritor` | harmless on its own; it's what makes the Agents Window reopen veritor as its worker workbench | open `~/projects/verity` as the Agents Window's primary workspace (option 2 above) | yes, same as option 2 |
| Worker projects dir `worker-data/…/projects/Users-danielreuter-projects-veritor` (transcripts, terminals) | harmless | none; a verity worker gets its own | no |

## 3. `~/.research`

| Item | Class | Fix | Disrupts? |
|---|---|---|---|
| `bin/research`: runs from `verity-main-wt/cli` with `main/.venv`, `RESEARCH_REPO=verity-main-wt/main` | already verity | none | — |
| `machines.toml` has two mentions, lines 34 and 1000: `/workspace/bin/veritor-zk-host-cuda`, pod name `vy-live2b-verifier-ro-veritor-campaign` | harmless (comments, real names) | none | — |
| `store.toml` | clean | — | — |
| `bin/chats-sync.sh:39` uses `~/.runpod/ssh/veritor-campaign-known_hosts` | harmless (a file name) | leave as is; rename only together with `runpod.py` | — |
| `bin/checkpoint_audit.sh`: greps `host="veritor` in `~/.veritor/exthost_mem.log` | functional for monitoring: it tracks the old chat's host, which is in the veritor workbench | after option 2, change it to match the new host label | no (script only) |
| notes and kb: `~/.veritor/*.log` paths in `LANE-CONTRACT.md`, `ops-tools.md`, `cursor-agent-host.md`; `pods-4090.md` title; two survey notes cite `projects/veritor` fallbacks | harmless (docs are correct about where the logs are) | none, or update wording later | no |
| Lane briefs and `STATE.md`s: no `projects/veritor` paths | clean | — | — |

## 4. `~/.runpod`

| Item | Class | Fix | Disrupts? |
|---|---|---|---|
| `ssh/veritor-campaign-known_hosts` (573 lines, written at 2:17 PM PT today) is used by `research`'s `pods/runpod.py:215` and `chats-sync.sh` | harmless name, **live file** | keep it. If renamed: add the new name as a symlink first, then change the code, then drop the old name. | a plain rename would break ssh host-key pinning for live lanes |
| `budget-*` / `deadman-*` / `watchdog-*` / `guardian.py` legacy files contain veritor strings | harmless (history) | none | — |
| `config.toml`, `ssh/` keys | clean | — | — |

## 5. Pod naming `*-veritor-campaign`

It's in `tools/research/src/research/pods/runpod.py:124` (`name = f"{args.name}-veritor-campaign"`) and in the `User-Agent`. Parsers also rely on it: `notes.py:91` (`POD_SUFFIX`), `connect.py:36`, `telemetry/policy/r17-rules-1.toml:6,56-58` (`project`, `cp-*/vc-*-veritor-campaign`), and `tests/test_notes.py`.
- **Functional coupling**: pod ownership, connect-by-name and telemetry all match on the suffix, and budget-cap prefixes match on names. Live pods (`vy-*`, `vyv-*`) carry the suffix.
- **Fix**: don't rename while pods are live. Later, in one verity PR: make the suffix a single constant, accept both `-veritor-campaign` and `-verity-campaign` in the parsers, then switch creation to the new suffix. Old pods age out.
- **Disrupts?** Changing only the creation side would orphan live pods from ownership and budget matching, so it's unsafe mid-run. Accepting both suffixes is safe.

## 6. Scripts, env, launchd, git remotes

| Item | Class | Fix | Disrupts? |
|---|---|---|---|
| launchd `com.veritor.memguardian` runs `~/.veritor/mem_guardian.py`. `MATCH` already includes `projects/verity` (so all verity worktrees are covered). | harmless name, working | none (rename optional; unload/reload briefly drops the guardian) | rename: brief gap |
| launchd `com.veritor.exthost-watch` writes to `~/.veritor/exthost_mem.log` | harmless name | none | — |
| launchd `com.research.chats-sync`, `podlane-sync`, `notes-watch` | clean (they use `~/.research`) | — | — |
| `~/.config/verity/r2.env`; no `~/.config/veritor`; no veritor in shell rc, `~/.gitconfig` or `~/.ssh/config` | clean | — | — |
| Git remotes: `veritor` → `danielreuter/veritor` (branch `vllm-poc`, 2751 commits ahead of origin, dirty). `verity`, `verity-main-wt/*` and `verity-wt/*` → `danielreuter/verity`. `verity` also has remote `sw57` (a pod). `veritor` also has about 20 prunable `/private/tmp` worktrees. | veritor checkout: functional (it's the worker cwd). Remotes: correct. | see item 1 and the preservation step below | — |

## 7. verity repo, runtime veritor references (at `main` ab9573fd)

Most hits (about 420 files) are **provenance comments or protocol identifiers**, for example gate sets `veritor.tc-ampere-bf16@2`, `veritor.int8-q7`, domain separator `veritor/indexed-domain/explicit/v1`, and `veritor/protocol/merkle/frame/v3`. They are hashed into digests and fixtures. **Don't rename them.** They're harmless in the sense that they don't point at the old repo.

Runtime items:

| Item | Class | Fix | Disrupts? |
|---|---|---|---|
| `integrations/vllm/verity_vllm/check/fold_compare.py:58` `DEFAULT_RECORD=/Users/danielreuter/projects/veritor/out/scale/e8/live/…`, used when `--record` is absent and the path exists | **functional**: reads data from the veritor checkout | copy the record into verity or the store, then point the default there or require `--record` | no |
| `integrations/vllm/tests/program/test_ship_roots.py:66` `SHIP_FALLBACK_REPO` defaults to `~/projects/veritor` | **functional (tests)**: builds `src.tgz` from veritor when the directory is missing | drop the fallback or skip | no |
| `tools/research/src/research/pods/mem_guard.py:29` `LANE_DIRS` includes `projects/veritor` but not verity | functional: the pod or laptop mem-guard ignores verity lane processes (if used; the launchd guardian is the separate `~/.veritor` one) | add `projects/verity` | no |
| `tools/research/src/research/pods/sh/pod_bootstrap.sh`: `REPO=$WORK/veritor`, `import veritor` | functional but apparently dead (nothing references it; the live bootstrap is `backends/sp1/pod_bootstrap.sh`) | delete it or port it | no |
| `notes.py:885` `GUARDIAN_LOG=~/.veritor/mem_guardian.log` | harmless (the real path) | none | — |
| `VERITOR_REPO` env var (vllm harness runners and tests) | harmless name; runners now set it from their own tree | optional rename with an alias | — |
| `veritor-zk-host` crate and `/workspace/bin/veritor-zk-host-cuda*` pod binaries | harmless names (a verity crate) | none mid-run | renaming breaks `VERITY_SP1_HOST` on live pods |

## Preserve before retiring the veritor checkout

- Uncommitted `zk/campaign/budget_cap.py` adds `rate_action="newest"`, which kills the newest pods first on a rate trip. **Verity's `budget_cap.py` has no `rate_action`**, and no note mentions it. I couldn't tell read-only which copy the `vyv-` budget daemon on `vy-control-verity` runs. The vLLM coordinator should confirm before anyone cleans veritor, and port the feature if it's live.
- Uncommitted `verity_ir/refs.py` (+303 lines) with `verity_ir/tests/test_refs_compose.py`, and the untracked `accumulation/` (437 files) and `out/capture/`: an owner needs to decide whether to port them or archive them.
- `vllm-poc` is 2751 commits ahead of `origin/vllm-poc`. Push it or bundle it for safekeeping.

## Proposed switchover sequence (non-disruptive first)

1. **Now, Daniel:** start the second worker for verity in a new clean worktree `~/projects/verity-agents`, using the commands in item 1, option 1. Confirm that the dashboard or My Machines shows two workers and that the new one's repo is `danielreuter/verity`. No effect on live work.
2. **Now, Daniel or the root:** launch all *new* coordinators and lanes on the verity worker ID. Existing agents stay on 5dae5d77.
3. **Now, as a verity PR (vLLM or research lane, merged by the research coordinator):** fix `fold_compare.py` `DEFAULT_RECORD`, `test_ship_roots.py` `SHIP_FALLBACK_REPO` and `mem_guard.py` `LANE_DIRS`. Make the pod suffix a constant and accept both `-veritor-campaign` and `-verity-campaign` without changing creation yet. Delete the dead `pods/sh/pod_bootstrap.sh`. None of this disrupts live work.
4. **Now, vLLM coordinator:** confirm which `budget_cap.py` the `vy-control-verity` daemon runs, and port `rate_action` into verity if it's the veritor copy.
5. **Daniel:** avoid Cursor updates and restarts, sign-out, and the My Machines toggle until step 7. Any of these can bounce or stop the veritor worker.
6. **After the old vLLM chat's five lanes and both laptop coordinators finish or move to the verity worker:** save the veritor leftovers (preservation list above), then **Daniel** switches the Agents Window's primary workspace from veritor to verity, or removes the veritor folder. That retires the veritor worker. Then update `checkpoint_audit.sh`'s host match.
7. **Later, optional:** switch pod creation to `-verity-campaign` once no `-veritor-campaign` pods are live. Rename the known_hosts file using the symlink approach. Rename the launchd labels and `~/.veritor`, which is cosmetic.
