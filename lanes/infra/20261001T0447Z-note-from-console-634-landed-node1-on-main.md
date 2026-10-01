# #634 landed; node 1's timer runs main's code

From console, 9:47 PM PDT.

- **Landed:** [verity #634](https://github.com/danielreuter/verity/pull/634) is on `main` (c1e920090, train C3).
- **Node 1 matches main:** `/workspace/research/console/{verity_console.py,util_collect.py}` are byte-identical to `tools/research/console/` at c1e920090, and the installed `verity-console.service` matches `infra/nebius/verity-console.service`. `MAIN_COMMIT` there records the commit. No unit change was needed.
- **No automatic fetch:** node 1 has no GitHub read access, so the timer can't fetch `main` itself. Until it can, console reinstalls from `main` after each console PR lands.
- **The `cursor/console-tool-558b` branch** has nothing unlanded and can go.
