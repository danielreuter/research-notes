#!/usr/bin/env bash
# Restore the resource steward's agent VM after a reset (idempotent, no secrets; reads RUNPOD_SSH_KEY_B64 from the env).
set -e
[ -s ~/.ssh/research_key ] || { mkdir -p ~/.ssh; install -m 600 /dev/null ~/.ssh/research_key; printf %s "$RUNPOD_SSH_KEY_B64" | base64 -d > ~/.ssh/research_key; }
for h in 81.85.2.165 81.85.2.121; do ssh-keygen -F $h >/dev/null || ssh-keyscan -t ed25519 $h 2>/dev/null >> ~/.ssh/known_hosts; done
[ -d ~/.research/notes/.git ] || git clone -q https://github.com/danielreuter/research-notes ~/.research/notes
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_UNMANAGED_INSTALL=/usr/local/bin sh
[ -d ~/wt/slack ] || { git -C /workspace fetch -q origin cursor/slack-coordination-6081 && git -C /workspace worktree add -q ~/wt/slack FETCH_HEAD; (cd ~/wt/slack && uv sync -q --all-packages --extra torch-cpu); }
mkdir -p ~/resource-steward && install -m 755 ~/.research/notes/lanes/resource-steward/tools/tick.sh ~/resource-steward/tick.sh
echo ok
