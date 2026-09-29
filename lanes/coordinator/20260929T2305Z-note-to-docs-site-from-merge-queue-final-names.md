---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: note · from: merge queue (bc-605d7c89) · to: the docs-site worker (bc-41cff24f) · created: 2026-09-29T23:05Z ·
repo: danielreuter/verity

# Note to the docs site: Daniel's final names, and the cases stage 1.5 builds against

**Not urgent. It changes no API answer.**

## 1. The final names, for user-facing labels

Daniel settled these with the diagram agent at about 4:00 PM PT:
- **Control (Vercel) is the API server and the Scheduler.**
  - The **API server** is the single entry point every client calls, and it issues every connection credential. It's what the last drafts called Access.
  - The **Scheduler** makes every allocation of compute: interactive (an agent's pod) and batch (a job). The queue is rows in the Database.
- **Compute (RunPod) is Interactive and Batch.** We build it ourselves, with no SkyPilot.
- **Console** (Approvals, Results) is a client of the API server.

Please use these on any user-facing label: admin page titles, nav, headings and help text. For example, "Batch jobs" on `/admin/jobs`, and "API server" wherever a page says Broker or Access.

**Code names stay:** `/api/jobs`, the `jobs` table, the `jobs:*` scopes and the cron paths. `docs/job-service-design.md` and the site spec use the new names from now on (spec, changes list item 4).

## 2. The cases stage 1.5 builds against have moved

Your report plans stage 1.5 on the 9 train cases at `d7272158`. Please build against these instead:

| File | Commit | Cases | SHA-256 |
|---|---|---|---|
| `train_vectors.json` | `b1089cf7` (unchanged at `ad6a06b1`) | 13 | `d92bcf435be90e6feb98d2138b824ba7a3dff9d54d395c52f3b773d68e368a97` |
| `vectors.json` | `8b2ee8a5` | 17 | `5138a64c36ff4e9dcdd140ad5562fbb905fed6726741abf4a1e9d1477696a53b` |

- **The 4 new train cases** are the Lean-record merges: spec §9.3, "Lean records", and the `regenerating` state in §9.4. GitHub's Merges API runs no custom merge driver, so the service ports #447's `tools/lean/merge.py` `merge()` and `audit.py`'s `text()`.
- **The job cases' new steps** pin your stricter bodies: `run_id`, `summary` and `slot` must be strings, and a body must be an object. Production should pass them as it is.
- **Spec item 10** now records what shipped: `/api/cron/…`, the test database, `tokens.actions`, `token_name` without a foreign key, and the `events` trigger.
