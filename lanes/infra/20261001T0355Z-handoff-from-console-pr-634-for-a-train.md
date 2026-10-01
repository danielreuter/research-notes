# For a train: verity #634 (console publisher, after #613)

From console, 8:55 PM PDT.

- **What:** [verity #634](https://github.com/danielreuter/verity/pull/634) (`cursor/console-raw-busy-a491`, off `main`). It's the one commit pushed to `cursor/console-tool-558b` after #613 landed in TCN2 at `ce31c4281`.
- **Contents:** raw GPU busy (util > 0) beside useful busy on both nodes; node 1 GPU-hours by holder; node 2 per-hour held and idle.
- **Status:** one file, `tools/research/console/verity_console.py`. It's byte-identical to the copy running on vy-nebius-1 since 03:47Z. The 16 repository tests pass. The sweep can delete `cursor/console-tool-558b`; nothing else on it is unlanded.
- **When it lands:** I'll point node 1's `verity-console` timer at `main` instead of the loose copy in `/workspace/research/console`. I'll send the unit change for `infra/nebius/verity-console.service` to you before touching the system unit.
