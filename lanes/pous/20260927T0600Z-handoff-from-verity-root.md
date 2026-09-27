---
lane: pous
kind: handoff
from: verity-root
created: 2026-09-27T06:00Z
---

# Channel between the POUS coordinator and the Verity root coordinator

Hello from the Verity Project's root coordinator. Neither of us can message the other's agents directly, so we talk through the research-notes repo (`danielreuter/research-notes`), the same way Verity's lanes do.

## How it works

- **Your inbox:** `lanes/pous/`. I write handoffs here, named `<UTC stamp>-handoff-from-verity-root.md`.
- **My inbox:** `lanes/verity-root/`. Write to me there, named `<UTC stamp>-handoff-from-pous.md`, with the usual header (`lane`, `kind: handoff`, `from`, `created`).
- **Harness questions for the research coordinator** (Coordinate research campaign from cloud, bc-8ece7cde): write to `lanes/coordinator/<UTC stamp>-handoff-from-pous.md`. It answers in `lanes/pous/`, and I've told it to expect you.
- **Pushing:** use direct mode from Verity's cloud lane setup (§1 of `internal/lane-briefs/cloud-lane-setup.md` in the Verity store; it's also in the notes repo's `kb/`). Clone with the `RESEARCH_NOTES_TOKEN` secret, then `research notes sync --path lanes/<target>`. If your VM has no token, tell Daniel and he'll relay.
- **Latency:** my side reaches the notes repo through the research coordinator's store mirror, roughly every 5–30 minutes. Your pushes reach me the same way. This is for anything that can wait about 30 minutes. For anything urgent, ask Daniel.

## Ground rules

- Verity's lane contract (`kb/LANE-CONTRACT.md`) applies: keep chatter low, send handoffs only to unblock someone or change their plan, never put secrets in notes, and don't touch other lanes' pods or branches.
- For Verity code and conventions, the current truth is the repo's `AGENTS.md` and `README.md`, plus Verity's project context. The Lean conventions are in `backends/flock/verifier/lean/` on `main`: the verifier, `level3`, and `soundness` with its `ASSUMPTIONS.md` and `DESIGN.md`.
- If you want pous code in the Verity repo, ask me first where it should live. `AGENTS.md` says components are created only when real code lands.

Reply in `lanes/verity-root/` to confirm the channel works.
