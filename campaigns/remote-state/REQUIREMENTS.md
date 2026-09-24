---
campaign: remote-state
created: 2026-09-24T20:10Z
status: user approved option (2) 2026-09-24 ~19:55Z; owner: the Project coordinator
---
> **Superseded (2026-09-24 1:20 PM PT) by the canonical `cloud-migration-requirements.md`:** laptop `~/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/cloud-migration-requirements.md`, cloud `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/cloud-migration-requirements.md`. Section 3.1 there lists which claims below held and which didn't.
# Remote state: any agent on any machine can run a lane; the laptop becomes optional

## Done means
1. An agent on a fresh machine (Cursor cloud VM, a server, a colleague's laptop) can run the whole lane loop with nothing
   from this laptop: read its brief and inbox, write checkpoints/reports, launch a pod job, register a result, check custody
   (`research data preserved`), render the tables.
2. No duty depends on the laptop being awake: the steward (stale lanes, idle-pod reaping, deadlines, budgets, the daily
   13:00Z render, kill routing) runs on an always-on host.
3. No evidence is silently lost or changed by the move: before any machine trusts the remote catalog, a catalog rebuilt from
   R2 alone on a fresh machine equals the laptop's catalog (same artifacts, attempts, labels, replicas), and every
   difference is explained. Records stay append-only.
4. Keys never enter git. Agents get them from Cursor secrets (done 2026-09-24: RUNPOD_API_KEY, RUNPOD_SSH_KEY_B64,
   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY = the R2 keys, R2_ENDPOINT / R2_BUCKET / R2_ACCOUNT_ID). Pods only get
   pod-scoped or short-lived minted credentials.
5. Two agents writing notes at the same time never lose each other's writes.
6. Still exactly one merger of main.

## What is laptop-only today, and the facts that size the work (checked 20:05Z)
| piece | today | note |
|---|---|---|
| notes (`~/.research/notes`) | local git, no remote | 0.9 GB on disk but the git repo is 14 MB: ~750 MB is gitignored proof fixtures under lanes/hints-fused-2, lanes/fp4-fast, lanes/red-team-leaf-3/evidence. Those belong in R2 as artifacts, not in notes. |
| artifact records (`~/.research/store`: manifests/ 115 MB, attempts/ 24 MB, labels/ 44 MB) | local, mostly copied to R2 | already append-only immutable files; remote keys are content-addressed (labels/<target>/<sha256>.json). catalog.sqlite (283 MB) is a disposable local index: `research data reindex --remote` rebuilds it from R2. Labels reach R2 only via an explicit `research data labels sync` (the P0 durability bug). |
| artifact files (objects/ 6.0 GB) | R2 + laptop cache | nothing to move once custody passes |
| run records (`~/.research/runs`, 5.7 GB) | fetched from pods to the laptop | some big overnight runs have no attempt record, so custody cannot verify them yet (e.g. r20260923-223427-9bab 1.2 GB) |
| pod registry (`~/.research/machines.toml`) | laptop | move into the notes repo or derive from RunPod pod names |
| code to pods | laptop uploads over the home link (vllm-rf-f1 hit the 10 min limit twice) | pods should fetch by commit |
| keys | laptop files (~/.runpod/config.toml, ~/.runpod/ssh/runpodctl-ssh-key, ~/.config/verity/r2.env) | tools must also read the env vars |
| steward (`com.research.notes-watch`) | laptop launchd | needs an always-on home |
| laptop-only helpers (mem guardian, exthost watch, nightly chats-sync) | laptop | stay; irrelevant off the laptop |

## Order (each step pays off on its own)
1. Notes to a private GitHub repo: move the gitignored fixtures to R2 first (register + preserve, then delete), add the
   remote, push; agents `git pull --rebase` before writing and push after. Per-lane timestamped files make conflicts rare;
   binding.json and checkpoint front matter are the only shared edits.
2. Keys from env: `research` reads RUNPOD_API_KEY when ~/.runpod/config.toml is absent and writes the SSH key from
   RUNPOD_SSH_KEY_B64; machines.toml moves into the notes repo.
3. Code to pods by commit, not from the uploader. Two designs; pick one and say why:
   (a) pods `git fetch` the commit from GitHub: needs a read-only GitHub token on every pod (a new pod credential) and lane
       commits pushed first;
   (b) the launcher puts `git archive <commit>` to R2 once (content-addressed by tree sha) and pods download it with the
       short-lived credentials `research data mint-credential` already makes: no new credential, unpushed commits work,
       and remote.py's digest/READY.json guarantees carry over.
4. Catalog remote-first: every write (put, label, attempt) goes to R2 at write time, not at a later sync (fixes the P0);
   then the parity test in "Done means" 3 on a fresh machine. Only after parity: machines stop needing the laptop's store.
5. Steward on an always-on host (the existing vy-control CPU pod at $0.03/h, or a small server): notes clone + R2 creds +
   RunPod key; the laptop's launchd copy is then stopped so there is one steward.
6. Then compare one lane on Cursor-managed cloud against one on an always-on My Machines server for a day: setup time,
   speed, cost, failures.

## Not in scope here
Colleague access and Team Pools; replacing Cursor.
