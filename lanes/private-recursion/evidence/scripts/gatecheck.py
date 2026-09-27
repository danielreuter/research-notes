import time, os, numpy as np
ART=os.environ.get('ART','/tmp/pr/arts')
from verity_flock.recursion import session as S, statement as T, vb, coins, witness as W, program as P
circ=T.parse_circuit(open(ART+'/d9837120/circuit.txt').read())
pub=T.load_public(ART+'/d9837120/pub-8.bin', circ)
st=T.Statement(circ,pub,T.load_comp(ART+'/04259cdd/comp.rows'))
fr=vb.Frame.of(st); prog=vb.build(fr)
sess=S.load_session(ART+'/bd9f7efb/honest'); tabs=coins.tables(fr,st,sess)
pubi,wit=W.convert(fr,st,st.C,pub,sess,tabs,rng=np.random.default_rng(7))
t=time.time(); r=P.evaluate(prog,{**tabs,**pubi,**wit},gate_sample=64,seed=1)
print('accepted',r.accepted,'gate-checked instances',r.gates,'s',round(time.time()-t,1))
