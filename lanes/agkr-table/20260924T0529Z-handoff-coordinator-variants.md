# If you see a more promising GKR variant than the one you are climbing, tell the coordinator: it gets its own lane

User (05:27Z): a more promising GKR variant can be hill-climbed as a new lane. If profiling or the design notes
(`backends/gkr/PROTOCOL.md` §14-15, the a-gpu / a-fusion / a-logup-union notes) point to a variant that could beat the
current path by a clear margin, write a handoff to `lanes/coordinator/` with the evidence and the rough plan. Keep your own
lane on the A100 cell meanwhile.
