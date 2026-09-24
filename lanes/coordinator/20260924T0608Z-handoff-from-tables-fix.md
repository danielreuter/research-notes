# One label moves the 4090 B-Ligero cell: art:68466c4a (instance-equiv) needs a non-producer's verified=accepted

From tables-fix, lane/tables-fix b11809c1 (gap A, gap B and the instance-equiv rule are in; render 06:02Z in
`~/.research/notes/lanes/tables-fix/20260924T0602Z-tables-render.md`).

`art:0d5b229a8c90c175a03068d2b2194670906aebff06787423ae75584b50c61e3e` (4090 FP8, B-Ligero v2 public selection, `t.total`
0.114 s = **3.0e6×**) fails the predicate for
one reason only: its instances are a re-packing. The equivalence `art:68466c4ad6b8197ea9624fb6b50037f5338e098a1cec9bfa03c014e86eb8c3f2`
(fused-phases) passes the content checks. It has no `verified=accepted` by a non-producer (producers: fused-phases,
r23-wave2-dev-4090). If someone who is neither of those re-checks it and labels it
`research data label art:68466c4a… verified=accepted`, the 4090 B-Ligero cell goes from 6.6e6× (art:cc59294a141e840789606a7d5d9a13c8d7654f29ef1bb11cf50f1702987f43a1, 0.252 s) to 3.0e6×,
with the footnote "instances re-packed; decoded values byte-identical to the frozen set (art:68466c4a…)".

The other 99 re-packed results with an equivalence also fail U (not independently verified) and/or P / X / K, so accepting
their equivalences alone changes no other cell. Decision for you: whether to have a non-producer verify art:68466c4a
before the 08:30Z render. No action needed from tables-fix either way.
