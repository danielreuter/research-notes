# Scope: user wants SP1-stock on ALL five targets; you keep A100 + the shared statement/guest/envelope, new lane sp1-formats does the other four

User (05:21Z): "SP1-stock and SP1-precompile ... populate these for all of our targets."

- You: A100 BF16 end to end, as launched. You own the shared pieces: the `relation-bare` statement (private x, W; public
  digest binding the instance identity and y), guest/host, and the bench-result envelope.
- New lane `sp1-formats` (base: your branch) ports fp8-ada, fp8-hopper, bf16-hopper and fp4-nvf4 arithmetic into NEW files
  under `backends/sp1/common/src/` and runs those four cells on H100 / 4090 / 5090.
- Please: (1) make the guest pick the format through one small dispatch point (an enum or format id carried in the
  statement), so sp1-formats only adds a module plus one match arm; (2) commit the statement + envelope + dispatch as early
  as you can (target 07:30Z) and write `lanes/sp1-formats/<ts>-handoff-from-sp1-table.md` with the tip sha and how to run a
  cell; (3) send them each later tip that changes shared code. Agree the dispatch shape with them if they ask first.
