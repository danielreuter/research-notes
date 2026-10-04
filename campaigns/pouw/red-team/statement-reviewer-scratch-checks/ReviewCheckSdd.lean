import Pouw
import Pouw.PearlC.V2HotChainOnly

open Pouw.PearlC
#check @witness_codes_differ
#print axioms Pouw.PearlC.witness_codes_differ
#print axioms Pouw.PearlC.witness_saltLive
#print axioms Pouw.PearlC.saltDeadP_card_le
#print axioms Pouw.PearlC.rhoD_atomMixP_flat
#print axioms Pouw.PearlC.atomMixChainP_saltLive_flat
#print axioms Pouw.PearlC.flatPairs_support
#print axioms Pouw.PearlC.pearlCGamma8192
#print axioms Pouw.PearlC.pearlCGamma16384
#print axioms Pouw.PearlC.ttOutPearlCWitness
#print axioms Pouw.PearlC.pearlCSampledSm120v2Cap1000_8192
#print axioms Pouw.PearlC.hotTileAccounting_sm120v2hot
example : SaltDead.support (SaltDead.flatLine fun _ => true, SaltDead.flatLineF fun _ => false) := ⟨_, _, rfl⟩
