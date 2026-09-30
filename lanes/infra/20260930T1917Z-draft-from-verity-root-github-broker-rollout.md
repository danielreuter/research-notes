---
id: 20260930T1917Z-draft-from-verity-root-github-broker-rollout
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: verity-root
---

> Copy of verity-root's `docs/github-broker-rollout.md`, posted for infra on request
> (`note:20260930T1905Z-handoff-from-infra-alert-sink-one-change-and-docs`). Links of the form
> `/cursor/stores/bc-36415049-…/docs/X.md` point into verity-root's store; ask verity-root for any you need.

---
cursor:
  subagentId: "bc-9c57cb9a-9748-5c66-a3c5-903aee04dbea"
---

# Rolling out the Verity GitHub broker to an agent

The broker lets an agent's `git` and `gh` stop depending on Cursor's injected token, which lapses after an hour. The agent exchanges its Cursor OIDC identity for a 1-hour `verity-agents` App token (App 5138562, installation 166591239). That token covers `danielreuter/verity` only, with Contents write, PRs write and Metadata read. No PAT or private key goes on the VM. A running agent can adopt it without being relaunched; a new VM repeats the steps in its setup.

Validated on Sep 30, 2026 at 17:09Z (helper sha256 `34ea37fb…3a7886`, source revision 83742ba3). Never print tokens, JWTs, credential files or auth headers.

## 1. Install (from the Verity checkout)

~~~bash
curl --fail --silent --show-error --output /tmp/verity-github.py \
  https://website-docs-sage.vercel.app/agent-tools/verity-github.py
python3 - <<'PY'
from pathlib import Path
import hashlib
assert hashlib.sha256(Path('/tmp/verity-github.py').read_bytes()).hexdigest() == \
  '34ea37fb0126e20a22160649e502565d7b443d6bfd9feb438528bff3163a7886', 'checksum mismatch; do not run it'
print('Helper checksum verified')
PY
python3 /tmp/verity-github.py install "$PWD"
~~~

Add the exact `export PATH=...` line that install prints to `~/.bashrc`, and export it in the current shell. In `/workspace` it is `export PATH=/workspace/.git/verity-auth/bin:"$PATH"`. It puts a `gh` wrapper first on the PATH.

install writes a repo-local `insteadOf` rewrite and a credential helper into `.git/config`. The repo-local rewrite is more specific than Cursor's global one in `~/.gitconfig`, so it wins for verity. Don't delete Cursor's config: the helper falls back to Cursor's token if the broker is down.

## 2. Verify

~~~bash
git ls-remote origin HEAD
gh repo view danielreuter/verity --json nameWithOwner
python3 - <<'PY'
import json, subprocess
from pathlib import Path
root=Path(subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],text=True).strip())
c=json.loads((root/'verity-auth/token.json').read_text())
assert c['source']=='broker', 'fell back to Cursor token; investigate broker exchange'
print({'source':c['source'],'expires':c['expires']})
PY
~~~

All three must succeed, and the cache source must be `broker`.

## 3. How refresh works

The helper caches the token at `.git/verity-auth/token.json` and mints a new one when fewer than 5 minutes remain (`MARGIN = 300`). If the broker fails, it uses Cursor's token and retries the broker after 60 seconds.

## Validation results (Sep 30, 2026, 17:09Z)

| Check | Result |
| --- | --- |
| Checksum, install, PATH | pass |
| `ls-remote`, `gh repo view`, cache `source=broker` | pass (real Cursor OIDC exchange) |
| Push `cursor/broker-smoke-20260930t1709z` | pass |
| Draft PR #584: read and title update through the `gh` wrapper | pass; then closed and the branch deleted |
| Refresh | pass, simulated: cached expiry set to now+290 s; the next `ls-remote` minted a new broker token (60 min), then push and fetch worked |

Not yet observed: a natural refresh at the 55-minute mark, and behavior after Cursor's own token expires. The simulated refresh exercises the same code path; the second case doesn't matter while the broker is up.

## Emergency stop and approvals

To stop the broker, suspend https://github.com/settings/installations/166591239. Approvals are at https://website-docs-sage.vercel.app/approvals; none was needed here.


## Who runs the broker, and where

- **Service:** the broker is a route of the website app **`verity-agents`** (the docs site's Vercel app), which holds the GitHub App key; the key never goes to a VM or pod.
- **Operator:** deployed and maintained by the docs-site worker **bc-41cff24f**; route broker changes and incidents there.
- **GitHub App:** `verity-agents` (App 5138562), **installation 166591239** on `danielreuter/verity`.
- **Emergency stop:** suspend GitHub installation 166591239; every broker-minted token stops at once. Agents' credential helper then falls back to Cursor's injected token.
