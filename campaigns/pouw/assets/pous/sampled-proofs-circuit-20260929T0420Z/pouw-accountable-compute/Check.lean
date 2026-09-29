import PouwAccountable

/-! The axioms of every theorem the notes cite (`lake env lean Check.lean`, output in AXIOMS.txt). The audit
(`tools/lean/audit.py`) checks every declaration independently of this file. -/

#print axioms PouwAccountable.soundWork_add_unsoundWork
#print axioms PouwAccountable.unsoundWork_singleton
#print axioms PouwAccountable.unsoundWork_le_harm
#print axioms PouwAccountable.Layout.harm_tile
#print axioms PouwAccountable.Layout.harm_xs
#print axioms PouwAccountable.Layout.harm_ys
#print axioms PouwAccountable.Layout.harm_node
#print axioms PouwAccountable.closureLaw_escape
#print axioms PouwAccountable.prCoin_fst
#print axioms PouwAccountable.both_escape_le
#print axioms PouwAccountable.harmOpt_isHarmBound
#print axioms PouwAccountable.harmOpt_le
#print axioms PouwAccountable.escape_lt_of_harm_gt
#print axioms PouwAccountable.choose_ratio_le_exp
#print axioms PouwAccountable.stratified_escape_le_exp
#print axioms PouwAccountable.stratified_isHarmBound
#print axioms PouwAccountable.audit_damage
#print axioms PouwAccountable.exfiltration
#print axioms PouwAccountable.audit_strata
#print axioms PouwAccountable.audit_closure
#print axioms PouwAccountable.accountable_compute
#print axioms PouwAccountable.compute_used
#print axioms PouwAccountable.compute_used_audit
#print axioms PouwAccountable.accountable_compute_floor
#print axioms PouwAccountable.harm_le_unsoundWork
#print axioms PouwAccountable.mem_closureLaw_draw
